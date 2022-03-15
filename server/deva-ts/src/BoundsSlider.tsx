// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
import { atom, selector } from 'recoil';
import { metadataState, constraintsState } from './Base';
import _ from "lodash";


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


// Heuristic for determining the precision of steps on the Slider 
export function getSliderStep(decimals) {
  if (decimals == null) { 
    return 1;
  }
  return Number((0.1 ** decimals).toFixed(decimals));
}

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


// {metric1: [min, max], metric2: [min, max]}
export const rangesState = selector({
  key: 'ranges',
  get: ({get}) => {
    const all = get(allCandidatesState);
    const metadata = get(metadataState);

    if (all === null) {
      return null;
    }

    const ranges = _.mapValues(metadata.metrics, (val, _obj) => {
        const min = val.range_min
        const max = val.range_max
        return [min, max];
      });

    return ranges;
  },
});


// higher is better map
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
