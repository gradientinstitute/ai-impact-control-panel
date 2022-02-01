import {useState, useEffect} from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import axios from 'axios';

import { roundValue, rvOperations } from './Widgets'
import { useRecoilState, useRecoilValue } from 'recoil';
import { Pane, paneState, scenarioState, 
        metadataState, constraintsState } from './Base';

import { allCandidatesState, maxRangesState, currentCandidatesState,
  filterCandidates, getSliderStep, bestValuesState,
  currentSelectionState} from './BoundsSlider';


const BackgroundColours = {
  0: 'gray-600',  // default
  1: 'gray-700',  // currentlySelected
}

function GetBackgroundColor(uid) {
    const blockStatus = useRecoilValue(currentCandidatesState)[uid];
    return "bg-" + BackgroundColours[blockStatus];
  };


export function BoundariesPane({}) {
    // name of current scenorio for url purposes e.g. "ezyfraud"
    const scenario = useRecoilValue(scenarioState);
    // largest possible ranges for specifying the scrollbar extents
    const maxRanges = useRecoilValue(maxRangesState);
    // list of currently permissible candidates based on current constraints
    const currentCandidates = useRecoilValue(currentCandidatesState);
    // the actual/current contraints as defined by the position of scrollbars
  
    // current constraints done by metric
    const [_costraints, setConstraints] = useRecoilState(constraintsState);
  
    // all candidates sent to us by the server
    const [_allCandidates, setAllCandidates] = useRecoilState(allCandidatesState);
  
    // initial loading of candidates
    useEffect(() => {
      const fetch = async () => {
        axios.get<any>("api/" + scenario + "/ranges")
          .then( response => response.data)
          .then( data => {
            setAllCandidates(data);
          });
      }
      fetch();
    }, []
    );
  
    // set initial value of the constraints
    useEffect(() => {
      setConstraints(maxRanges)
    }, [maxRanges]);
  
    if (currentCandidates === null) {
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

  // return (
  //   <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-10 grid-cols-1 text-center items-center pb-10">
  //     <h1>Boundaries Placeholder</h1>
  //     Your content here. We may need to fix the step numbering above.
  //     <Slider {...100}>
  //       slider
  //     </Slider>

  //   </div>
  // );
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
    const uid = x[0];
    const u: any = x[1];
    const lowerIsBetter = u.lowerIsBetter === false ? false : true;
    
    const range_min = u.range_min
    const range_max = u.range_max

    const pane = (u.type === "qualitative") ? 

      (<QualitativeConstraint x={x} 
        constraints={constraints}
        uid={uid}
        lowerIsBetter={lowerIsBetter}
        range_min = {range_min}
        range_max = {range_max}/>) :

      (<QuantitativeConstraint x={x}
        constraints={constraints}
        uid={uid}
        lowerIsBetter={lowerIsBetter}
        range_min = {range_min}
        range_max = {range_max}/>)

    return (
      <div >
        {pane}
      </div>
    );
  });

  return (
    <div className="grid grid-cols-1 gap-4">
      {items}
    </div>
  );
}


function QualitativeConstraint({x, constraints, uid, lowerIsBetter, range_min, range_max}) {
  const u: any = x[1];
  const min = range_min
  const max = range_max
  const cmin = constraints[uid][0];
  const cmax = constraints[uid][1];
//   const bgcolor = GetBackgroundColor(uid);

  const options = (u.options).slice(min, max + 1);

  const marks = Object.fromEntries(
    options.map(x => [u.options.indexOf(x), x])
  )

  const name = u.name;
  const allowed = options
    .filter(x => (u.options.indexOf(x) >= cmin && u.options.indexOf(x) <= cmax))
    .map(x => (<p>{x}</p>));

  const notAllowed = options
  .filter(x => !(u.options.indexOf(x) >= cmin && u.options.indexOf(x) <= cmax))
  .map(x => (<p>{x}</p>));

  return (
    <div      
      className="col-span-10 text-center">{name}

      <p className="col-span-3 my-auto">{}</p>
      <div className="col-span-2 text-center">
      <p className="font-bold">Allowed</p>
      <p>{allowed}</p>
      </div>

      <div className="col-span-2 text-center">
      <p className="font-bold">Not Allowed</p>
      <p>{notAllowed}</p>
      </div>
      <p className="col-span-3 my-auto">{}</p>

      <p className="col-span-2 my-auto">{}</p>

      <p className="col-span-2 my-auto">{}</p>

    </div>
  )
}


function QuantitativeConstraint({x, constraints, uid, lowerIsBetter, range_min, range_max}) {
  // TODO: remember how to specify these types in destructuring args
  const u: any = x[1];
//   const vals = maxRanges[uid];
  const sign = lowerIsBetter ? 1 : -1;
  const min = range_min
  const max = range_max
  const min_string = u.prefix + " " + (lowerIsBetter ? min : max * sign) + " " + u.suffix;
  const max_string = u.prefix + " " + (lowerIsBetter ? max : min * sign) + " " + u.suffix;
  const name = u.name;

  const cmin = lowerIsBetter ? constraints[uid][0] : constraints[uid][1];
  const cmax = lowerIsBetter ? constraints[uid][1] : constraints[uid][0];
  
  const cstring = u.prefix + " (" + (cmin * sign) + " - " + (cmax * sign) + ")\n" + u.suffix;
  const decimals = u.displayDecimals;
  const bgcolor = GetBackgroundColor(uid);

  return (
    <div key={uid} 
    className={"grid grid-cols-5 gap-8 " + bgcolor + " rounded-lg p-4"}>
      
      <h2 className="col-span-5 text-center">{name}</h2>
      <p className="col-span-5 text-3xl">{cstring}</p>

      <p className="col-span-1 text-xs text-right my-auto">{min_string}</p>
      <div className="col-span-3 my-auto">
        <RangeConstraint uid={uid} min={min} max={max} marks={null} decimals={decimals} lowerIsBetter={lowerIsBetter}/>
      </div>
      <p className="col-span-1 text-xs text-left my-auto">{max_string}</p>
    </div>
  )
}


function RangeConstraint({uid, min, max, marks, decimals, lowerIsBetter}) {

  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const [currentSelection, setCurrentSelection] = useRecoilState(currentSelectionState);

  const all = useRecoilValue(allCandidatesState);
  const thresholdValues = useRecoilValue(bestValuesState);
  const val = constraints[uid][1];

  function onBeforeChange() {
    setCurrentSelection(uid);
  };

  function onChange(newVal: any) {

    // copy constraints into a new object
    let n = {...constraints};

    n[uid] =  [n[uid][0], newVal]

    // check how many candidates are left
    const withNew = filterCandidates(all, n);

    if (withNew.length ===  0) {
      // if the constraints exceeds the threshold value 
      // set to the threshold value
      // find the threshold step to return
      const stepSize = getSliderStep(decimals);
      const stepsFromMin = Math.ceil((thresholdValues.get(uid) - min) / stepSize);
      newVal = roundValue(
        rvOperations.floor, 
        (stepsFromMin * stepSize) + min, 
        decimals
      );
      
      n[uid]  = [n[uid][0], newVal];
    }

    setConstraints(n);  
  }
  

  let rangeProps = {
    min: min,
    max: max,
    onBeforeChange: onBeforeChange,
    onChange: onChange,
    allowCross: false,
    value: val,
  //   step: getSliderStep(decimals),
    trackStyle: {backgroundColor: "lightblue"},
    railStyle: {backgroundColor: "gray"},
    reverse: !lowerIsBetter,
  };
  
  // for qualitative metrics
  if (marks !== null) {
    rangeProps["marks"] = marks;
    rangeProps["step"] = null;
  }

  return (
    <div>
      <Slider {...rangeProps} />
      <OptimalDirection lowerIsBetter={lowerIsBetter}/>
    </div>
    );
  }


function OptimalDirection({lowerIsBetter}) {
    const leftColour= lowerIsBetter ? "text-green-500" : "text-red-500";
    const rightColour = lowerIsBetter ? "text-red-500" : "text-green-500";
    const leftText = lowerIsBetter ? "most optimal" : "least optimal";
    const rightText = lowerIsBetter ? "least optimal" : "most optimal";
  
    return (
      <div className="grid grid-cols-4">
        <div className={"col-span-2 text-left text-s " + leftColour}>
         <p><i>← {leftText}</i></p>
        </div>
        <div className={"col-span-2 text-right text-s " + rightColour}>
          <p><i>{rightText} →</i></p>
        </div>
      </div>
    );
  }


function StartButton({}) {

  const [submit, setSubmit] = useState(false);

  const scenario = useRecoilValue(scenarioState);
  const constraints = useRecoilValue(constraintsState);
  const [_pane, setPane] = useRecoilState(paneState);

  useEffect(() => {
    const fetch = async () => {
      await axios.put<any>("api/" + scenario + "/constraints", constraints);
      setPane(Pane.Pairwise);
    }
    if (submit) {
      fetch();
    }
  }, [submit]
  );

  return (
      <button className="bg-gray-200 text-black rounded-lg" 
        onClick={() => {setSubmit(true)}}>
        <div className="p-4 text-5xl">
          Next
        </div>
      </button>
  );
}
