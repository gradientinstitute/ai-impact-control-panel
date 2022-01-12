import 'rc-slider/assets/index.css';
import { atom, selector } from 'recoil';
import { metadataState } from './Base';
import _ from "lodash";
import { std } from 'mathjs';
import { roundValue, rvOperations } from './Widgets';
import { allCandidatesState, currentCandidatesState } from './Constrain';

enum blockingStates {
  'default',
  'blocked',
  'bounced',
  'blocking',
}

export const lastBouncedState = atom({
  key: 'lastBounced',
  default: null,
});

export const scrollbarHandleState = atom({
  key: 'scrollbarHandleState',
  default: null,
});

export const scrollbarsState = selector({
  key: 'scrollbarsState',
  get: ({get}) => {
      const all = get(allCandidatesState);
      const metadata = get(metadataState);
      
      if (all === null) {
      return null;
      }
      
      const ranges = _.mapValues(metadata.metrics, (_obj) => {
      return blockingStates.default;
      });
      return ranges;
  },
})

// // Returns the most optimal values for each metric given possible candidates
export const bestValuesState = selector({
  key: 'optimalMetricValues',
  get: ({get}) => {
    const currentCandidates = get(currentCandidatesState);
    let currOptimal = new Map();
    currentCandidates.forEach((candidate) => {
      Object.entries(candidate).forEach(([metric, value]) => {
        const currVal = value as number;
        let currOpt = currOptimal.get(metric);
        currOpt = (typeof currOpt == 'undefined') ? Number.MAX_SAFE_INTEGER : currOpt;
        currOptimal.set(metric, currVal < currOpt ? currVal : currOpt); 
      });
    });
    return currOptimal;
  }
});

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

// Toggles whether metrics are blocked or not given their current candidates
export function setBlockedMetrics(n, m, activeOptimal, uid, bounced,
  lastBounced, setLastBounced, decimals) {

  // check the current metric
  if (bounced) {
    setLastBounced(uid);
  } else if (bounced == uid) {
    setLastBounced(null);
  }

  // check if another change has resolved the most recent bounce
  if (lastBounced != null) {
    
    const bounds = Object.values(Object.fromEntries(Object.entries(n)
      .filter(([key]) => key.match(lastBounced))))[0];
    
    const optimal = isOptimal(activeOptimal, lastBounced, 
      decimals, bounds);

    if (!(optimal)) {
      lastBounced = null;
      setLastBounced(lastBounced);
    }
  }

  // mark as default, blocked, or bounced
  Object.entries(n).forEach(([metric, bounds]) => {

    const optimal = isOptimal(activeOptimal, metric, decimals, bounds);
    
    const stillBlocking = (lastBounced !== uid && lastBounced != null) 
      && (m[metric] === blockingStates.blocking);

    m[metric] = stillBlocking ? m[metric] : blockingStates.default; 
    m[metric] = optimal && !stillBlocking ? blockingStates.blocked : m[metric];
    m[metric] = lastBounced === metric ? blockingStates.bounced : m[metric];

  })

  return lastBounced;
}

// Determines if a metric is at its optimal position 
function isOptimal(activeOpt, uid, decimals, bounds) {
  return roundValue(rvOperations.ceil, activeOpt.get(uid), decimals) >= bounds[1];
}

// euclidean distance with scaled features for making scrollbar suggestions
function weightedEucDistance(a, b, weight) {
  return a
    .map((x, i) => Math.abs(weight[i] * (x-b[i]))**2)
    .reduce((sum, now) => sum + now)
    ** (1/2);
}

// filter for all states where the constraint can be made better
function getPossibleCandidates(all, activeOptimal, uid) {
  let possibleCandidates = new Array();
  Object.values(all).forEach((candidate) => {
    if (candidate[uid] < activeOptimal.get(uid)) {
      possibleCandidates.push(Object.values(candidate));
    }
  });
  return possibleCandidates;
}

// Returns the least invasive candidate for scrollbar unblocking
// this heuristic can be modified
function getBestUnblockingCandidates(possibleCandidates, currPosition, metricImportance) {

  let bestCandidates = new Object({
    'eucDistance': Number.MAX_SAFE_INTEGER, 
    'targetCandidates': new Array()
  });
  
  /* The algorithm calculates the euclidean distance between 
    - the vector of the current constraints set by the user and 
    - the optimal position for possible candidates where the constraints can
      be tightened along a certain metric
    Then, it chooses the least invasive potential candidates and suggests 
    changes for thresholds that are blocking the last bounce from improving 
  */
  const currentPositionVector = Object.values(currPosition);
  possibleCandidates.forEach(possibleCandidateVector => {
    const dist = weightedEucDistance(possibleCandidateVector, 
      currentPositionVector, metricImportance);
    if (dist < bestCandidates['eucDistance']) {
      bestCandidates = new Object({
        'eucDistance': dist, 
        'targetCandidates': new Array(possibleCandidateVector)
      });
    } else if (dist == bestCandidates['eucDistance']) {
      bestCandidates['targetCandidates'].push(possibleCandidateVector);
    }
  });
  return bestCandidates;
}

// Toggles suggestions to loosen constraints on metrics that are blocking
// the last bounce from improving 
export function setBlockingMetrics(n, m, uid, activeOptimal, 
  all, lastBounced, metricImportance) {

  if (uid != lastBounced) return;

  const possibleCandidates = getPossibleCandidates(all, activeOptimal, uid);

  const currPosition = _.mapValues(n, (val) => {
    return val[1];
  });
  
  const bestCandidates = getBestUnblockingCandidates(possibleCandidates, 
    currPosition, metricImportance);

  if (bestCandidates['targetCandidates'] === []) return;
  
  // make suggestions for metrics to unblock
  Object.entries(currPosition).forEach(([key, val], i) => {
    bestCandidates['targetCandidates'].forEach(candidate => {
      const canBeRelaxed = val < candidate[i];
      m[key] = canBeRelaxed ? blockingStates.blocking : m[key];  
    })
  });
}
