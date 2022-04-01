// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
import { atom, selector } from 'recoil';
import { allCandidatesState, metadataState, constraintsState, 
         configState } from './Base';
import _ from "lodash";
import { roundValue, rvOperations } from './Widgets';
import { compareConfig } from './Config';
import { currentSelectionState, currentCandidatesState } from './BoundsSlider';


export enum blockingStates {
  'default',
  'blocked',
  'blocking',
  'resolvedBlock',
  'currentlySelected',
  'blockedMetric',
  'threshold'
}

export const blockedStatusState = selector({
  key: 'blockedStatusState',
  get: ({get}) => {
    const constraints = get(constraintsState);
    const uidSelected = get(currentSelectionState);
    const isBlocked = get(isBlockedState);
    const blockingMetrics = get(blockingMetricsState).blockingMetrics;
    const blockedMetric = get(blockedMetricState);
    const resolvedBlock = get(resolvedBlockedState);
    const atThreshold = get(atThresholdState);

    const state = _.mapValues(constraints, (cons, uid, _obj) => {
      // pick which constraint is changing
      let status = blockingStates.default;
      if (blockedMetric === uid && !resolvedBlock) {
        status = blockingStates.blockedMetric;
      } else if (blockedMetric === uid && resolvedBlock) {
        status = blockingStates.resolvedBlock;
      } else if (blockingMetrics.has(uid) && !resolvedBlock) {
        status = blockingStates.blocking;
      } else if (uidSelected === uid && isBlocked) {
        status = blockingStates.blocked;
      } else if (uidSelected === uid && atThreshold) {
        status = blockingStates.threshold;
      } else if (uidSelected === uid) {
        status = blockingStates.currentlySelected;
      } 
      return status;
    });
    return state;
  }
})

// Metric to unblock as selected by the user
// Suggestions for unblocking are made relative to this metric 
export const blockedMetricState = atom({
  key: 'blockedMetric',
  default: null,
});

// snapshot of hte current constraint state when the 'unblock metrics' button
// is clicked. used for making unblocking suggestions for the target bar
export const blockedConstraintsState = atom({
  key: 'blockedconstraints',
  default: null,
});

// Heuristic for determining the precision of steps on the Slider 
export function getSliderStep(decimals) {
  if (decimals == null) { 
    return 1;
  }
  return Number((0.1 ** decimals).toFixed(decimals));
}

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

// return candidates where the blocked metric constraint can be improved
export const potentialUnblockingCandidatesState = selector({
  key: 'potentialUnblockingCandidates',
  get: ({get}) => {
    const uid = get(blockedMetricState);
    if (uid === null) return [];        
    const all = get(allCandidatesState);
    const constraints = get(constraintsState);
    return all.filter(candidate => candidate[uid] < constraints[uid][1]);
  }
});

// returns whether or not the blocked metric has been unblocked
export const resolvedBlockedState = selector({
  key: 'resolvedBlocked',
  get: ({get}) => {
    const metadata = get(metadataState);

    let uid = get(blockedMetricState);
    if (uid === null) {
      return true;
    }
    const constraints = get(constraintsState);
    const all = get(allCandidatesState);
    const step = getSliderStep(metadata.metrics[uid].displayDecimals);

    let n = {...constraints};
    const curr = constraints[uid][1];
    const newVal = curr - step;

    if (newVal < metadata.metrics[uid].min) {
      return true;
    }
    
    n[uid]  = [n[uid][0], newVal];

    // check how many candidates are left
    const withNew = filterCandidates(all, n);
    return !(withNew.length === 0);
  }
});

// returns whether or not the currently selected metric is blocked
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

    if (newVal < metadata.metrics[uid].min) {
      return false;
    }

    n[uid]  = [n[uid][0], newVal];
    
    // check how many candidates are left
    const withNew = filterCandidates(all, n);
    return (withNew.length === 0);
  }
});


// returns whether or not the currently selected metric is at 
// the min/max threshold based on data provided (but not blocked)
// used for range_min/range_max visualisations
export const atThresholdState = selector({
  key: 'atThresholdState',
  get: ({get}) => {
    const metadata = get(metadataState);
    const uid = get(currentSelectionState);
    if (uid === null) {
      return false;
    }

    const constraints = get(constraintsState);
    const step = getSliderStep(metadata.metrics[uid].displayDecimals);
    const curr = constraints[uid][1];
    const newVal = curr - step;
    
    if (newVal < metadata.metrics[uid].min) {
      return true;
    }

    return false;
  }
});

// Returns maps required for determining whether metrics are blocked
// and the associated target values/candidates
export const blockingMetricsState = selector({
  key: 'blockingMetrics',
  get: ({get}) => {
    const uidBlocked = get(blockedMetricState);
    const constraints = get(blockedConstraintsState);
    const potentialCandidates = get(potentialUnblockingCandidatesState);
    
    let blockingMetrics = new Map();
    let suggestedCandidates = new Map();

    if (uidBlocked === null) {
      return {blockingMetrics, suggestedCandidates};
    }

    let blockingMaps = getBlockingMaps(potentialCandidates, constraints);
    // map of metrics to set of target values
    blockingMetrics = blockingMaps.blockingMetrics;
    // map of candidates to set of metrics and target values
    suggestedCandidates = blockingMaps.suggestedCandidates;

    // filter out metrics and models that are not a factor in unblocking
    let models = Array.from(suggestedCandidates)
      .map(x => x[0])
      .map(candidate => filteredCandidate(candidate, blockingMetrics, constraints, uidBlocked));

    models = removeNonPareto(models);
    blockingMaps = getBlockingMaps(models, constraints)
    blockingMetrics = blockingMaps.blockingMetrics;
    suggestedCandidates = blockingMaps.suggestedCandidates;
    return {blockingMetrics, suggestedCandidates};
  }
});

function removeNonPareto(models) {

  let dominated = new Array(models.length);
  for (let i = 0; i < dominated.length; i++) {
    dominated[i] = false;
  }

  for (let [i, m] of models.entries()) {
    for (let [j, n] of models.entries()) {

      if (dominated[i] === true)
        break;
      
      if (dominated[j] === true || i === j)
        continue;
      
      const mArray = Object.entries(m);
      const d = mArray.every(([a,v]) => m[a] >= n[a]) && 
                mArray.some(([a,v]) => m[a] > n[a]);

      dominated[i] = d ? true : dominated[i];
    }
  }

  let efficient = [...models];
  dominated.forEach((dom, index) => {
    efficient[index] = (dom === true) ? null : efficient[index]
  });

  return efficient.filter(x => x != null);
}

function getBlockingMaps(potentialCandidates, constraints) {
  const blockingMetrics = new Map();
  const suggestedCandidates = new Map();

  // determine which other metrics need to be adjusted for change to happen
  potentialCandidates.forEach(candidate => {
    (Object.entries(candidate)).forEach(([metric, targetValue]) => {
      if (targetValue > constraints[metric][1]) {

        // map of metrics to set of target values
        // used for calculating the minimum required to potentially unblock
        if (!blockingMetrics.has(metric)) {
          blockingMetrics.set(metric, new Set([{targetValue, candidate}]));
        } else {
          blockingMetrics.get(metric).add({targetValue, candidate});
        }
        
        // map of candidates to set of metrics and target values
        // used for calculating the minimum required to definitey unblock
        if (!suggestedCandidates.has(candidate)) {
          suggestedCandidates.set(candidate, new Set([{metric, targetValue}]));
        } else {
          suggestedCandidates.get(candidate).add({metric, targetValue});
        }
      }
    });
  });

  return {blockingMetrics, suggestedCandidates};
}

// Eliminate variables that do not affect blocking by setting them to 
// the current constraint. Used for filtering for efficient set for unblocking
function filteredCandidate(candidate, blockingMetrics, constraints, uidBlocked) {
  let modifiedCandidate = new Map(Object.entries(candidate));
  const keys = Object.keys(candidate);
  keys.forEach(key => {
    if (!blockingMetrics.has(key)) {
      // the metric is not blocking
      modifiedCandidate.set(key, constraints[key][1]);
    } else if (modifiedCandidate.get(key) < constraints[key][1]) {
      // the candidate value for a particular metric is already included 
      // with the current constraint setting
      modifiedCandidate.set(key, constraints[key][1]);
    }
  });
  return Object.fromEntries(modifiedCandidate);
}

// determine the value required to definitely unblock a metric
// without needing to adjust other sliders
export const unblockValuesState = selector({
  key: 'unblockValues',
  get: ({get}) => {
    const blockingMetrics = get(blockingMetricsState).suggestedCandidates;

    // filter for candidates only one metric needs improvement
    const m = (Array.from(blockingMetrics))
      .map(x => x[1])
      .filter(x => x.size === 1);

    // take the smallest value required to unblock blockedMetric
    let unblockingMetrics = new Map();
    m.forEach(([x, y]) => {
      if (!(unblockingMetrics.has(x.metric))) {
        unblockingMetrics.set(x.metric, x.targetValue);
      } else if (unblockingMetrics.get(x.metric) >= x.targetValue) {
        unblockingMetrics.set(x.metric, x.targetValue);
      }
    });
    return unblockingMetrics;
  }
});

// maximum possible ranges (doesnt change)
// {metric1: [min, max], metric2: [min, max]}
export const maxRangesState = selector({
  key: 'maxRanges',
  get: ({get}) => {
    const all = get(allCandidatesState);
    const metadata = get(metadataState);
    const configs = get(configState);

    if (all === null) {
      return null;
    }

    let ranges = getDataMinMax(metadata, all);
    if (compareConfig(configs, "minMaxDisplay", "display visual min/max")) {
      ranges = getVisualMinMax(metadata);
    }

    return ranges;
  },
});


function getDataMinMax(metadata, all) {
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
}

function getVisualMinMax(metadata) {
  const ranges = _.mapValues(metadata.metrics, (val, uid, _obj) => {
    return [val.visual_min, val.visual_max];
  });
  return ranges;
}

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
