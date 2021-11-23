import React, {useState, useEffect, useReducer, useContext} from 'react';
import Slider, { Range } from 'rc-slider';
import 'rc-slider/assets/index.css';
import { atom, selector, useRecoilState, useRecoilValue } from 'recoil';
import {Pane, paneState, scenarioState, metadataState } from './Base';
import axios from 'axios';
import _ from "lodash";




// server payload
export const payloadState = atom({  
  key: 'payload', 
  default: null, 
});

// the CURRENT state of the contraints
export const constraintsState = atom({  
  key: 'constraints', 
  default: null, 
});

// the highlight status of the range sliders
export const highlightState = atom({
  key: 'highlight',
  default: null,
})

// list of all the candidates
export const allCandidatesState = selector({  
  key: 'allCandidates', 
  get: ({get}) => {
    const p = get(payloadState);
    if (p === null) {
      return null;
    }
    return p.points;
  },
});

// list of all the candidates grouped by metric
export const allMetricsState = selector({  
  key: 'allMetrics', 
  get: ({get}) => {
    const p = get(payloadState);
    if (p === null) {
      return null;
    }
    return p.collated;
  },
});

// maximum possible ranges (doesnt change)
export const maxRangesState = selector({
  key: 'maxRanges',
  get: ({get}) => {
    const all = get(allMetricsState);
    if (all === null) {
      return null;
    }
    const items = _.mapValues(all, (val, _uid, _obj) => {
      const min = Math.min(...val);
      const max = Math.max(...val);
      return [min, max];
    });
    return items;
  },
});

function filterCandidates(candidates, bounds) {
  const items = candidates.filter( (c) => {
      return Object.entries(c).every(([k, v]) => {
        const lower = v >= bounds[k][0];
        const upper = v <= bounds[k][1];
        return lower && upper
      });
    });
  return items;
}

// filter all the candidates to just the ones
// permissable by the currently selectede ranges
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


export const currentDirectionsState = selector({
  key: 'currentDirections',
  get: ({get}) => {
    const curr = get(constraintsState);
    const range = get(maxRangesState);
    const met = get(allMetricsState);
    const all = get(allCandidatesState);

    const res = _.mapValues(met, (val, uid, _obj) => {
      let minval = range[uid][0];
      let maxval = range[uid][1];

      let n = {...curr};
      n[uid] = minval;
      const low = filterCandidates(all, n).length > 0;
      n[uid] = maxval;
      const high = filterCandidates(all, n).length > 0;
      return [low, high];
    });
  },
});


export function ConstraintPane({}) {

  const scenario = useRecoilValue(scenarioState);
  const metadata = useRecoilValue(metadataState);
  const maxRanges = useRecoilValue(maxRangesState);
  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const curr = useRecoilValue(currentCandidatesState);
  const [_payload, setPayload] = useRecoilState(payloadState);
  const [highlights, setHighlight] = useRecoilState(highlightState);
  
  // initial loading of candidates
  useEffect(() => {
    const fetch = async () => {
      const result = await axios.get<any>(scenario + "/ranges");
      setPayload(result.data);
    }
    fetch();
  }, []
  );
      
  // update constraints when we get ranges
  useEffect(() => {
    setConstraints(maxRanges);
    }, [maxRanges]
  );

  // update highlights when we get ranges
  useEffect(() => {
    if (maxRanges !== null) {
      const items = _.mapValues(maxRanges, _x => {
        return [false, false];
      });
      setHighlight(items);
    }
  });

  if (curr === null) {
    return (<div>Loading...</div>);
  }


  return (
    <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-10 grid-cols-1 text-center items-center pb-10">
      <h1>Constraint Pane</h1>
      <div>
        <ConstraintStatus />
      </div>
      <div className="mb-10">
        <MultiRangeConstraint />
      </div>
      <div className="width-1/4">
        <StartButton />
      </div>
    </div>
  );
}

function ConstraintStatus({}) {
  
  const curr = useRecoilValue(currentCandidatesState);
  const all = useRecoilValue(allCandidatesState);

  return (
  <div className="rounded-lg bg-green-700 p-4 my-auto">
    <h2 className="text-2xl">{curr.length} of {all.length}</h2>
    <p>candidate models remain</p>
  </div>
  );

}

function MultiRangeConstraint({}) {
  const metadata = useRecoilValue(metadataState);
  const maxRanges = useRecoilValue(maxRangesState);
  const constraints = useRecoilValue(constraintsState);

  if (maxRanges === null || constraints === null) {
    return (<div>Loading...</div>);
  }

  const items = Object.entries(metadata.metrics).map((x) => {
    // TODO: remember how to specify these types in destructuring args
    const uid = x[0];
    const u: any = x[1];
    const vals = maxRanges[uid];
    const min = vals[0];
    const max = vals[1];
    const cmin = constraints[uid][0];
    const cmax = constraints[uid][1];
    const cstring = u.prefix + " (" + cmin + " - " + cmax + ")\n" + u.suffix;
    const min_string = u.prefix + " " + min + " " + u.suffix;
    const max_string = u.prefix + " " + max + " " + u.suffix;
    const name = u.name;
    return (
      <div key={uid} className="grid grid-cols-5 gap-8 bg-gray-600 rounded-lg p-4">
        <h2 className="col-span-5 text-center">{name}</h2>
        
        <p className="col-span-5 text-3xl">{cstring}</p>

        <p className="col-span-1 text-xs text-right my-auto">{min_string}</p>
        <div className="col-span-3 my-auto">
          <RangeConstraint uid={uid} min={min} max={max}/>
        </div>
        <p className="col-span-1 text-xs text-left my-auto">{max_string}</p>
      </div>
    );
  });

  return (
    <div className="grid grid-cols-1 gap-4">
      {items}
    </div>
  );
}

function RangeConstraint({uid, min, max}) {
  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const val = constraints[uid];
  const [rangeProps, setRangeProps] = useState({}); 
  const all = useRecoilValue(allCandidatesState);
  const [highlights, setHighlights] = useRecoilState(highlightState);
  const h = highlights[uid];

  function onChange(x: any) {
    let n = {...constraints};
    const oldval = n[uid];
    n[uid] = x;
    const withNew = filterCandidates(all, n);
    if (withNew.length == 0) {
      n[uid] = oldval;
    }
    setConstraints(n)
  }

  function onBeforeChange(x: any) {
    let newh = [];
    for (const uid in highlights) {
      newh.push([true, true]);
    }
    setHighlights(newh);
  }

  function onAfterChange(x: any) {
    const nn = _.mapValues(highlights, (_x) => {return [true, true]});
    setHighlights(nn);
  }

  let hstylelow = {};
  let hstylehigh = {};
  if (h[0]) {
    hstylelow = {backgroundColor: "black", borderColor: "red"};
  }
  if (h[1]) {
    hstylehigh = {backgroundColor: "black", borderColor: "red"};
  }
  
  
  // Dodgy, dodgy hack
  // https://github.com/react-component/slider/issues/366
  // TODO: try different library?
  useEffect(() => {
    
    const baseProps = {
      min: min,
      max: max,
      onBeforeChange: onBeforeChange,
      onChange: onChange,
      onAfterChange: onAfterChange,
      allowCross: false,
      handleStyle: [hstylelow, hstylehigh],
    };
    const vProps = {...baseProps, value: [...val]};
    setRangeProps(vProps);
    window.requestAnimationFrame(() => {
      setRangeProps(baseProps)});

  }, [constraints])

  return (
  <div>
    <Range {...rangeProps} />
  </div>
  );
}

function StartButton({}) {

  const [pane, setPane] = useRecoilState(paneState);
  
  return (
      <button className="bg-gray-200 text-black rounded-lg" 
        onClick={() => {setPane(Pane.Pairwise)}}>
        <div className="p-4 text-5xl">
          Next
        </div>
      </button>
  );
}

