import { atom, selector } from 'recoil';
import { std } from 'mathjs';
import { metadataState, constraintsState } from './Base';
import _ from "lodash";
import {roundValue, rvOperations} from './Widgets';

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

// // Returns the most optimal values for each metric given possible candidates
// // {metric1: <most desirable value in current candidate set>, etc.}
export const bestValuesState = selector({
  key: 'optimalMetricValues',
  get: ({get}) => {
    const currentCandidates = get(currentCandidatesState);
    const higherIsBetterMap = get(higherIsBetterState);

    let currOptimal = new Map();
    currentCandidates.forEach((candidate) => {
      Object.entries(candidate).forEach(([key, value]) => {
        const val = value as number;
        const defaultValue = higherIsBetterMap[key]
          ? Number.MIN_SAFE_INTEGER 
          : Number.MAX_SAFE_INTEGER;
        const storedValue = (typeof currOptimal[key] != 'undefined') 
          ? currOptimal.get(key) 
          : defaultValue;
        const lowerValue = val < storedValue ? val : storedValue;
        const higherValue = val > storedValue ? val : storedValue;
        const optimalValue = higherIsBetterMap[key] ? higherValue : lowerValue;
        currOptimal.set(key, optimalValue);
      })
    })
    return currOptimal;
  }
})

// All states where the constraint can be made better
export const potentialUnblockingCandidatesState = selector({
  key: 'potentialUnblockingCandidates',
  get: ({get}) => {
    const all = get(allCandidatesState);
    const metadata = get(metadataState);
    const activeOptimal = get(bestValuesState);
    const uid = get(currentSelectionState);
  
    if (uid === null) {
      return [];
    }

    const higherIsBetter = metadata.metrics[uid].higherIsBetter;

    let possibleCandidates = [];
    Object.values(all).forEach((candidate) => {
      const isBetter = higherIsBetter
        ? candidate[uid] > activeOptimal.get(uid) 
        : candidate[uid] < activeOptimal.get(uid);
      if (isBetter) {
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
    const metricImportance = get(metricImportanceState);

    const currPosition = _.mapValues(n, (val, key, _obj) => {
      const higherIsBetter = metadata.metrics[key].higherIsBetter;
      return higherIsBetter ? val[0] : val[1];
    });
    
    const currentPositionVector = Array.from(Object.values(currPosition));
    let bestCandidates = {
      'eucDistance': Number.MAX_SAFE_INTEGER, 
      'targetCandidates': []
    };
    
    // The algorithm calculates the euclidean distance between 
    //   - the vector of the current constraints set by the user and 
    //   - the optimal position for possible candidates where the constraints can
    //     be tightened along a certain metric
    //   Then, it chooses the least invasive potential candidates and suggests 
    //   changes for thresholds that are blocking the last bounce from improving 

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
});

export const higherIsBetterState = selector({
  key: 'higherIsBetter',
  get: ({get}) => {
    const metadata = get(metadataState);
    const higherIsBetterMap = _.mapValues(metadata.metrics, (val, uid, _obj) => {
      return val.higherIsBetter;
    });
    return higherIsBetterMap;
  }
})

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
      if ((uidSelected === uid) && isBlocked) {
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
    const higherIsBetter = get(higherIsBetterState);
    const all = get(allCandidatesState);
    const step = getSliderStep(metadata.metrics[uid].decimals);

    let n = {...constraints};
    if (higherIsBetter[uid]) {
      const curr = constraints[uid][0];
      const newVal = curr + step;
      n[uid] = [newVal, n[uid][1]];
    } else {
      const curr = constraints[uid][1];
      const newVal = curr - step;
      n[uid]  = [n[uid][0], newVal];
    }
    
    // check how many candidates are left
    const withNew = filterCandidates(all, n);
    return (withNew.length == 0);
  }
});

// maximum possible ranges (doesnt change)
// {metric1: [min, max], metric2: [min, max]}
// note whether max is good or bad depends on higherIsBetter
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
      const decimals = 'decimals' in val ? val.decimals : 0; 
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

