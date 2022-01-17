import { atom, selector } from 'recoil';
import { std } from 'mathjs';
import { metadataState, constraintsState } from './Base';
import _ from "lodash";
import { roundValue, rvOperations } from './Widgets';

export enum blockingStates {
  'default',
  'blocked',
  'willHelp',
  'couldHelp',
  'wontHelp',
}

export const currentSelectionState = atom({
  key: 'currentSelection',
  default: null,
});

// Metric to unblock as selected by the user
// Suggestions for unblocking are made relative to this metric 
export const blockedMetricState = atom({
  key: 'blockedMetric',
  default: null,
});

// info from the ranges API containing
// array containing all of the candidates
// [{metric1: value1, metric2: value1}, {metric1: value3, metric2:value4}]
export const allCandidatesState = atom({  
  key: 'allCandidates', 
  default: null, 
});

// Euclidean distance with scaled features for making scrollbar suggestions
function weightedEucDistance(a, b, weight) {
  return a
    .map((x, i) => Math.abs(weight[i] * (x-b[i]))**2)
    .reduce((sum, now) => sum + now)
    ** (1/2);
}

// Heuristic for determining the precision of steps on the Slider 
export function getSliderStep(decimals) {
  if (decimals == null) { 
    return 1;
  }
  return Number((0.1 ** decimals).toFixed(decimals));
}

// // For metric scaling used in suggesting scrollbar blockers to adjust
export const metricImportanceState = selector({
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

// uses filterCandidates to give list of candidates
// permissable by the currently selected ranges
export const currentCandidatesState = selector({
  key: 'currentCandidates',
  get: ({get}) => {
    const allCandidates = get(allCandidatesState);
    const constraints = get(constraintsState);
    if (allCandidates === null || constraints === null) {
      return null;
    }
    return filterCandidates(allCandidates, constraints);
  },
});

// Returns the most optimal values for each metric given possible candidates
// {metric1: <most desirable value in current candidate set>, etc.}
export const bestValuesState = selector({
  key: 'optimalMetricValues',
  get: ({get}) => {
    const currentCandidates = get(currentCandidatesState);
    let currOptimal = new Map();
    currentCandidates.forEach((candidate) => {
      Object.entries(candidate).forEach(([metric, value]) => {
        let currVal = value as number;
        let currOpt = currOptimal.get(metric);
        currOpt = (typeof currOpt == 'undefined') ? Number.MAX_SAFE_INTEGER : currOpt;
        currOptimal.set(metric, currVal < currOpt ? currVal : currOpt); 
      });
    });
    return currOptimal;
  }
});

// All states where the constraint can be made better
export const potentialUnblockingCandidatesState = selector({
  key: 'potentialUnblockingCandidates',
  get: ({get}) => {
    const all = get(allCandidatesState);
    const activeOptimal = get(bestValuesState);
    const uid = get(currentSelectionState);
  
    if (uid === null) {
      return [];
    }

    let possibleCandidates = [];
    Object.values(all).forEach((candidate) => {
      if (candidate[uid] < activeOptimal.get(uid)) {
        possibleCandidates.push(Object.values(candidate));
      }
    });
    return possibleCandidates;
  }
});

// Returns the least invasive candidate for scrollbar unblocking
// this heuristic can be modified
export const bestUnblockingCandidatesState = selector({
  key: 'bestUnblockingCandidates',
  get: ({get}) => {

    const possibleCandidates = get(potentialUnblockingCandidatesState);
    const metadata = get(metadataState);
    const n = get(constraintsState);

    const currPosition = _.mapValues(n, (val, key, _obj) => {
      return val[1];
    });
    
    const currentPositionVector = Array.from(Object.values(currPosition));
 
    return null;
  }
});

// Stores the current 'state' of each scrollbar with the blocking status
// {metric1: <value from blockingStates enum>, metric2: etc.}
// const scrollbarHandleState = atom({
//   key: 'scrollbarHandleState',
//   default: null,
// });
export const scrollbarHandleState = selector({
  key: 'scrollbarHandleState',
  get: ({get}) => {
    const constraints = get(constraintsState);
    const uidSelected = get(currentSelectionState);
    const isBlocked = get(isBlockedState);
    // colour test
    const state = _.mapValues(constraints, (cons, uid, _obj) => {
      // pick which constraint is changing
      let m = blockingStates.default;
      if (uidSelected === uid && isBlocked) { 
        m = blockingStates.blocked;
      }
      return m;
    });
    return state;
  }
})

export const isBlockedState = selector({
  key: 'isBlockedState',
  get: ({get}) => {
    const metadata = get(metadataState);
    const uid = get(currentSelectionState);
    if (uid === null) {
      return false;
    }
    const constraints = get(constraintsState);
    const all = get(allCandidatesState);
    const step = getSliderStep(metadata.metrics[uid].displayDecimals);

    let n = {...constraints};
    const curr = constraints[uid][1];
    const newVal = curr - step;
    n[uid]  = [n[uid][0], newVal];
    
    // check how many candidates are left
    const withNew = filterCandidates(all, n);
    return (withNew.length === 0);
  }
});

// maximum possible ranges (doesnt change)
// {metric1: [min, max], metric2: [min, max]}
export const maxRangesState = selector({
  key: 'maxRanges',
  get: ({get}) => {
    const all = get(allCandidatesState);
    const metadata = get(metadataState);

    if (all === null) {
      return null;
    }
    
    const ranges = _.mapValues(metadata.metrics, (val, uid, _obj) => {
      // doesn't exist in the qualitative metrics
      const decimals = val.displayDecimals != null ? val.displayDecimals : 0; 
      const tvals = all.map(x => x[uid]);
      // TODO: deal with stuff like this in the server
      const min = roundValue(rvOperations.floor, Math.min(...tvals), decimals); 
      const max = roundValue(rvOperations.ceil, Math.max(...tvals), decimals); 
      return [min, max];
    });
    return ranges;
  },
});

// higher is better map (doesnt change)
// return only candidates that are within the supplied bounds
export function filterCandidates(candidates, bounds) {
  const items = candidates.filter( (c) => {
      return Object.entries(c).every(([k, v]) => {
        const lower = v >= bounds[k][0];
        const upper = v <= bounds[k][1];
        return lower && upper
      });
    });
  return items;
}
