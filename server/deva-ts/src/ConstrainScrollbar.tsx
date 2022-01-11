import 'rc-slider/assets/index.css';
import { atom, selector, useRecoilValue } from 'recoil';
import { constraintsState, metadataState } from './Base';
import _ from "lodash";
import { std } from 'mathjs';
import { roundValue, rvOperations } from './Widgets';
import { allCandidatesState, currentCandidatesState, higherIsBetterState } from './Constrain';

export enum blockingStates {
  'default',
  'blocked',
  'bounced',
  'blocking',
}

// the metric that was last bounced or null if none bounced
// string of metric name
export const lastBouncedState = atom({
  key: 'lastBounced',
  default: null,
});

// Stores the current 'state' of each scrollbar with the blocking status
// {metric1: <value from blockingStates enum>, metric2: etc.}
export const scrollbarHandleState = atom({
  key: 'scrollbarHandleState',
  default: null,
});

// mapping from metric to the values required to unblock the last bounced
// {metric1: [value1, value2, value3, ...] metric2: etc }
export const targetsState = atom({
  key: 'targets',
  default: null,
});

// // mapping from metric to the state of its handle 
// // i.e. default, blocked, blocking, bounced  
// TODO re-ithkn this, it's acting as a (possibly wrong) default
export const scrollbarsState = selector({
  key: 'scrollbarsState',
  get: ({get}) => {
      const all = get(allCandidatesState);
      const metadata = get(metadataState);
      
      if (all === null) {
        return null;
      }
      
      const states = _.mapValues(metadata.metrics, (_obj) => {
        return blockingStates.default;
      });
      return states;
  },
})

// Returns the most optimal values for each metric given possible candidates
// {metric1: <most desirable value in current candidate set>, etc.}
export const bestValuesState = selector({
  key: 'optimalMetricValues',
  get: ({get}) => {
    const currentCandidates = get(currentCandidatesState);
    const higherIsBetterMap = get(higherIsBetterState);
    let currOptimal = new Map();
    currentCandidates.forEach((candidate) => {
      Object.entries(candidate).forEach(([key, value]) => {
        const val = value as number;
        const defaultValue = higherIsBetterMap.get(key) 
          ? Number.MIN_SAFE_INTEGER 
          : Number.MAX_SAFE_INTEGER;
        const storedValue = (typeof currOptimal.get(key) != 'undefined') 
          ? currOptimal.get(key) 
          : defaultValue;
        const lowerValue = val < storedValue ? val : storedValue;
        const higherValue = val > storedValue ? val : storedValue;
        const optimalValue = higherIsBetterMap.get(key) ? higherValue : lowerValue;
        currOptimal.set(key, optimalValue);
      })
    })
    return currOptimal;
  }
})

// For metric scaling used in suggesting scrollbar blockers to adjust
export const getMetricImportance = selector({
  key: 'metricImportance',
  get: ({get}) => {
    const all = get(allCandidatesState);
    const metadata = get(metadataState);
    const importance = _.mapValues(metadata.metrics, (val, uid, _obj) => {
      const tvals = all.map(x => x[uid]);
      return 1 / std([...tvals]);
    });    
    return Object.values(importance);
  }
})

// Heuristic for determining the precision of steps on the Slider 
export function getSliderStep(decimals) {
  if (decimals == null) { 
    return 1;
  }
  return Number((0.1 ** decimals).toFixed(decimals));
}

// Helper function which ceils/floors numbers to the specified decimal places
export function getRounded(higherIsBetterMap, uid, val, decimals) {
  return higherIsBetterMap.get(uid) 
    ? roundValue(rvOperations.floor, val, decimals) 
    : roundValue(rvOperations.ceil, val, decimals);
}

// Toggles whether metrics are blocked or not given their current candidates
export function setBlockedMetrics(n, m, uid, higherIsBetterMap, activeOptimal, 
  bounced, lastBounced, setLastBounced, decimals, setTargets) {

  // check the current metric
  if (bounced) {
    setLastBounced(uid);
  } else if (bounced === uid) {
    setLastBounced(null);
    setTargets(null);
  }

  // check if another change has resolved the most recent bounce
  if (lastBounced != null) {
    
    const bounds = Object.values(Object.fromEntries(Object.entries(n)
      .filter(([key]) => key.match(lastBounced))))[0];
    
    const optimal = isOptimal(higherIsBetterMap, activeOptimal, lastBounced, 
      decimals, bounds);

    if (!(optimal)) {
      lastBounced = null;
      setLastBounced(lastBounced);
      setTargets(null);
    }
  }

  // mark as default, blocked, or bounced
  Object.entries(n).forEach(([metric, bounds]) => {

    const optimal = isOptimal(higherIsBetterMap, activeOptimal, metric, 
      decimals, bounds);
      
    const stillBlocking = (lastBounced !== uid && lastBounced != null) 
      && (m[metric] === blockingStates.blocking);

    m[metric] = stillBlocking ? m[metric] : blockingStates.default; 
    m[metric] = optimal && !stillBlocking ? blockingStates.blocked : m[metric];
    m[metric] = lastBounced === metric ? blockingStates.bounced : m[metric];

    // TODO: make active optimal update on change 
  })

  return lastBounced;
}

// Determines if a metric is at its optimal position / threshold
function isOptimal(higherIsBetterMap, activeOptimal, uid, decimals, bounds) {
  return higherIsBetterMap.get(uid) 
    ? roundValue(rvOperations.floor, activeOptimal.get(uid), decimals) <= bounds[0]
    : roundValue(rvOperations.ceil, activeOptimal.get(uid), decimals) >= bounds[1]
}

// Euclidean distance with scaled features for making scrollbar suggestions
function weightedEucDistance(a, b, weight) {
  return a
    .map((x, i) => Math.abs(weight[i] * (x-b[i]))**2)
    .reduce((sum, now) => sum + now)
    ** (1/2);
}

// Filter for all states where the constraint can be made better
function getPossibleCandidates(all, higherIsBetterMap, activeOptimal, uid) {
  let possibleCandidates = [];
  Object.values(all).forEach((candidate) => {
    const isBetter = higherIsBetterMap.get(uid) 
      ? candidate[uid] > activeOptimal.get(uid) 
      : candidate[uid] < activeOptimal.get(uid);
    if (isBetter) {
      possibleCandidates.push(Object.values(candidate));
    }
  });
  return possibleCandidates;
}

// Returns the least invasive candidate for scrollbar unblocking
// this heuristic can be modified
function getBestUnblockingCandidates(possibleCandidates, currPosition, metricImportance) {
  const currentPositionVector = Array.from(currPosition.values());
  
  let bestCandidates = {
    'eucDistance': Number.MAX_SAFE_INTEGER, 
    'targetCandidates': []
  };
  
  /* The algorithm calculates the euclidean distance between 
    - the vector of the current constraints set by the user and 
    - the optimal position for possible candidates where the constraints can
      be tightened along a certain metric
    Then, it chooses the least invasive potential candidates and suggests 
    changes for thresholds that are blocking the last bounce from improving 
  */
  possibleCandidates.forEach(possibleCandidateVector => {
    const dist = weightedEucDistance(possibleCandidateVector, 
      currentPositionVector, metricImportance);
    if (dist < bestCandidates['eucDistance']) {
      bestCandidates = {
        'eucDistance': dist, 
        'targetCandidates': new Array(possibleCandidateVector)
      };
    } else if (dist === bestCandidates['eucDistance']) {
      bestCandidates['targetCandidates'].push(possibleCandidateVector);
    }
  });
  return bestCandidates;
}

// Toggles suggestions to loosen constraints on metrics that are blocking
// the last bounce from improving and returns an array with the optimal
// positions to move the blocking metrics to
export function setBlockingMetrics(n, m, uid, higherIsBetterMap, activeOptimal, 
  all, lastBounced, metricImportance, setTargets, decimals) {

  if (uid !== lastBounced) return;

  const possibleCandidates = getPossibleCandidates(all, higherIsBetterMap, 
    activeOptimal, uid);

  const currPosition = new Map();
  Object.entries(n).forEach(([key, val]) => {
    currPosition.set(key, higherIsBetterMap.get(key) ? val[0] : val[1]);
  });
  
  const bestCandidates = getBestUnblockingCandidates(possibleCandidates, 
    currPosition, metricImportance);

  if (bestCandidates['targetCandidates'] === []) return;
  
  // make suggestions for metrics to unblock
  let t = {}
  Array.from(currPosition).forEach(([key, val], i) => {
    let metricTarget = [];
    bestCandidates['targetCandidates'].forEach(candidate => {
      const canBeRelaxed = higherIsBetterMap.get(key)
        ? val > candidate[i]
        : val < candidate[i]
      m[key] = canBeRelaxed ? blockingStates.blocking : m[key];
      metricTarget.push(canBeRelaxed ? candidate[i] : null);
    });
    t[key] = metricTarget;
  });

  setTargets(t);
  return t;
}
