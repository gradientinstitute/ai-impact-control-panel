import React, {useState, useEffect, useReducer, useContext} from 'react';
import Slider, { Range } from 'rc-slider';
import 'rc-slider/assets/index.css';
import { atom, selector, useRecoilState, useRecoilValue } from 'recoil';
import {Pane, paneState, scenarioState, metadataState } from './Base';
import axios from 'axios';
import _ from "lodash";

export const constraintsState = atom({  
  key: 'constraints', 
  default: null, 
});

export const allCandidatesState = atom({  
  key: 'allCandidates', 
  default: null, 
});

export const maxRangesState = selector({
  key: 'maxRanges',
  get: ({get}) => {
    const metadata = get(metadataState);
    const allCandidates = get(allCandidatesState);

    if (allCandidates === null) {
      return null;
    }

    const items = _.mapValues(metadata.metrics, (_val, uid, _obj) => {
      const vals = allCandidates.collated[uid];
      const min = Math.min(...vals);
      const max = Math.max(...vals);
      return [min, max];
    });
    return items;
  },
});

export function ConstraintPane({}) {

  const scenario = useRecoilValue(scenarioState);
  const metadata = useRecoilValue(metadataState);
  const [allCandidates, setAllCandidates] = useRecoilState(allCandidatesState);
  const maxRanges = useRecoilValue(maxRangesState);
  const [constraints, setConstraints] = useRecoilState(constraintsState);
  
  // initial loading of candidates
  useEffect(() => {
    const fetch = async () => {
      const result = await axios.get<any>(scenario + "/ranges");
      setAllCandidates(result.data);
    }
    fetch();
  }, []
  );
      
  // update constraints when we get ranges
  useEffect(() => {
    setConstraints(maxRanges);
    }, [maxRanges]
  );


  return (
    <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-10 grid-cols-1 text-center items-center pb-10">
      <h1>Constraint Pane</h1>
      <div className="mb-10">
        <MultiRangeConstraint />
      </div>
      <div className="width-1/4">
        <StartButton />
      </div>
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
  
  function onChange(x: any) {
    setConstraints((old: any) => {
      let n = {...old};
      n[uid] = x;
      return n;
    });
  }
  
  // Dodgy, dodgy hack
  // https://github.com/react-component/slider/issues/366
  // TODO: try different library?
  useEffect(() => {
    setRangeProps({
      value: [...val],
      min: min,
      max: max,
      onChange: onChange,
      allowCross: false,
      });
    window.requestAnimationFrame(() => {
      setRangeProps({
        min: min,
        max: max,
        onChange: onChange,
        allowCross: false,
      });
    });
  }, [val])

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

