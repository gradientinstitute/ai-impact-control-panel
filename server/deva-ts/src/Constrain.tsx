import {useState, useEffect} from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import axios from 'axios';
import _ from "lodash";

import { useRecoilState, useRecoilValue } from 'recoil';
import {Pane, paneState, scenarioState, 
        metadataState, constraintsState } from './Base';

import { maxRangesState, currentCandidatesState, allCandidatesState,
  currentSelectionState, higherIsBetterState, isBlockedState,
  bestUnblockingCandidatesState, scrollbarHandleState, filterCandidates,
  getSliderStep, } from './ConstrainScrollbar';

enum HandleColours {
  'white',  // default
  'gray',   // blocked
  'orange', // bounced
  'red',    // blocking
}

export function ConstraintPane({}) {

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

    const pane = (u.type === "qualitative") ? 

      (<QualitativeConstraint x={x} 
        maxRanges={maxRanges} 
        constraints={constraints}
        uid={uid}/>) :

      (<QuantitativeConstraint x={x}
        maxRanges={maxRanges}
        constraints={constraints}
        uid={uid}/>)

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

function QuantitativeConstraint({x, maxRanges, constraints, uid}) {
  // TODO: remember how to specify these types in destructuring args
  const u: any = x[1];
  const vals = maxRanges[uid];
  const min = vals[0];
  const max = vals[1];
  const min_string = u.prefix + " " + min + " " + u.suffix;
  const max_string = u.prefix + " " + max + " " + u.suffix;
  const name = u.name;
  const cmin = constraints[uid][0];
  const cmax = constraints[uid][1];
  const cstring = u.prefix + " (" + cmin + " - " + cmax + ")\n" + u.suffix;
  const decimals = 'decimals' in u ? u.decimals : null; 
  const currentSelection = useRecoilValue(currentSelectionState);
  const bgcolor = currentSelection === uid ? 'bg-yellow-800' : 'bg-gray-700';

  return (
    <div key={uid} 
    className={"grid grid-cols-5 gap-8 " + bgcolor + " rounded-lg p-4"}>
      
      <h2 className="col-span-5 text-center">{name}</h2>
      <p className="col-span-5 text-3xl">{cstring}</p>

      <p className="col-span-1 text-xs text-right my-auto">{min_string}</p>
      <div className="col-span-3 my-auto">
        <RangeConstraint uid={uid} min={min} max={max} marks={null} decimals={decimals}/>
      </div>
      <p className="col-span-1 text-xs text-left my-auto">{max_string}</p>
    </div>
  )
}

function QualitativeConstraint({x, maxRanges, constraints, uid}) {
  const u: any = x[1];

  const min = 0;
  const max = u.options.length - 1; 

  const cmin = constraints[uid][0];
  const cmax = constraints[uid][1];
  const currentSelection = useRecoilValue(currentSelectionState);
  const bgcolor = currentSelection === uid ? 'bg-yellow-800' : 'bg-gray-700';

  const options = Object.fromEntries(
    u.options.map(x => [u.options.indexOf(x), x])
  )

  const name = u.name;
  const allowed = u.options
    .filter(x => (u.options.indexOf(x) >= cmin && u.options.indexOf(x) <= cmax))
    .map(x => (<p>{x}</p>));

  const notAllowed = u.options
  .filter(x => !(u.options.indexOf(x) >= cmin && u.options.indexOf(x) <= cmax))
  .map(x => (<p>{x}</p>));

  return (
    <div key={uid} 
    className={"grid grid-cols-10 gap-8 " + bgcolor + " rounded-lg p-4 pb-10"}>
            
      <h2 className="col-span-10 text-center">{name}</h2>

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
      <div className="col-span-6 my-auto">
        <RangeConstraint uid={uid} min={min} max={max} marks={options} decimals={null}/>
      </div>
      <p className="col-span-2 my-auto">{}</p>

    </div>
  )
}

function RangeConstraint({uid, min, max, marks, decimals}) {

  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const [currentSelection, setCurrentSelection] = useRecoilState(currentSelectionState);

  const all = useRecoilValue(allCandidatesState);

  const higherIsBetterMap = useRecoilValue(higherIsBetterState);
  const higherIsBetter = higherIsBetterMap[uid];
  const val = higherIsBetter ? constraints[uid][0] : constraints[uid][1];

  const isBlocked = useRecoilValue(isBlockedState);
  const blockString = (currentSelection === uid) && (isBlocked) ? "BLOCKED" : "";

  const bestCandidates = useRecoilValue(bestUnblockingCandidatesState);
  
  function onBeforeChange() {
    setCurrentSelection(uid);
  }

  function onChange(newVal: any) {

    // copy constraints into a new object
    let n = {...constraints};
    // set the bounds of the scrollbar
    n[uid] = higherIsBetter ? [newVal, n[uid][1]] : [n[uid][0], newVal];

    // check how many candidates are left
    const withNew = filterCandidates(all, n);
    if (withNew.length > 0) {
      setConstraints(n);
    }
  }
  
  const blockedScrollbar : any = useRecoilValue(scrollbarHandleState);
  const handleStyle = {
    backgroundColor: HandleColours[blockedScrollbar[uid]], 
    height: 20, 
    width: 20, 
    borderColor: HandleColours[blockedScrollbar[uid]]
  };

  let rangeProps = {
    min: min,
    max: max,
    onBeforeChange: onBeforeChange,
    onChange: onChange,
    // onAfterChange: onAfterChange,
    allowCross: false,
    value: val,
    step: getSliderStep(decimals),
    handleStyle: handleStyle, 
    trackStyle: higherIsBetter ? {backgroundColor: "gray"} : {backgroundColor: "lightblue"},
    railStyle: higherIsBetter ? {backgroundColor: "lightblue"} : {backgroundColor: "gray"},
  };
  
  // for qualitative metrics
  if (marks !== null) {
    rangeProps["marks"] = marks;
    rangeProps["step"] = null;
  }

  // const percentage = getTargetPercentage(higherIsBetterMap, uid, targets, min, max, decimals);
  // const blockingState = {...blockedScrollbar}[uid];

  return (
  <div>
    {/* <BlockingTargetBar percentage={percentage} blockingState={blockingState}/> */}
    <p>{"Blocked status: " + blockString}</p>
    <Slider {...rangeProps} />
    <OptimalDirection higherIsBetter={higherIsBetter}/>
  </div>
  );
}

function OptimalDirection({higherIsBetter}) {
  const leftColour = higherIsBetter ? "text-red-500" : "text-green-500";
  const rightColour = higherIsBetter ? "text-green-500" : "text-red-500";
  const leftText = higherIsBetter ? "least optimal" : "most optimal";
  const rightText = higherIsBetter ? "most optimal" : "least optimal";

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

// function getTargetPercentage(higherIsBetterMap, uid, targets, min, max, decimals) {
//   let target = null;
//   let percentage = higherIsBetterMap.get(uid) ? 100 : 0;

//   if (targets != null && targets[uid] != null) {
//     target = targets[uid]
//       .map(x => getRounded(higherIsBetterMap, uid, x, decimals))
//       .filter(x => x != null);
//     percentage = higherIsBetterMap.get(uid) 
//       ? ((Math.max(...target) - min) / (max - min)) * 100
//       : ((Math.min(...target) - min) / (max - min)) * 100;
//   }
//   return percentage;
// }

// function BlockingTargetBar({percentage, blockingState}) {

//   let colour = "border-gray-600";
//   colour = blockingState == blockingStates.blocking ? "border-red-500" : colour;
//   colour = blockingState == blockingStates.bounced ? "border-yellow-500" : colour;

//   return (
//     <div className="w-full flex">
//       <div className={"h-6 min-h-full border-r-4 bg-gray-600 " + colour} style={{width:percentage + "%"}}></div>
//       <div className={"h-6 min-h-full bg-gray-600"} style={{width:(100-percentage) + "%"}}> </div>
//     </div>
//   );
// }


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
