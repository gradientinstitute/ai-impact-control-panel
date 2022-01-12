import {useState, useEffect} from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { atom, selector, useRecoilState, useRecoilValue } from 'recoil';
import {Pane, paneState, scenarioState, 
        metadataState, constraintsState } from './Base';
import axios from 'axios';
import _ from "lodash";
import {roundValue, rvOperations} from './Widgets';
import { std } from 'mathjs';

// import {blockingStates, getMetricImportance, lastBouncedState, scrollbarHandleState, 
//         setBlockedMetrics, setBlockingMetrics, scrollbarsState, 
//         bestValuesState, getSliderStep, targetsState, getRounded} from './ConstrainScrollbar';

// Euclidean distance with scaled features for making scrollbar suggestions
function weightedEucDistance(a, b, weight) {
  return a
    .map((x, i) => Math.abs(weight[i] * (x-b[i]))**2)
    .reduce((sum, now) => sum + now)
    ** (1/2);
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

// // Returns the least invasive candidate for scrollbar unblocking
// // this heuristic can be modified
// function getBestUnblockingCandidates(possibleCandidates, currPosition, metricImportance) {
  
  
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

// Heuristic for determining the precision of steps on the Slider 
function getSliderStep(decimals) {
  if (decimals == null) { 
    return 1;
  }
  return Number((0.1 ** decimals).toFixed(decimals));
}

// Helper function which ceils/floors numbers to the specified decimal places
function getRounded(higherIsBetterMap, uid, val, decimals) {
  return higherIsBetterMap.get(uid) 
    ? roundValue(rvOperations.floor, val, decimals) 
    : roundValue(rvOperations.ceil, val, decimals);
}


enum blockingStates {
  'default',
  'blocked',
  'willHelp',
  'couldHelp',
  'wontHelp',
}

// Stores the current 'state' of each scrollbar with the blocking status
// {metric1: <value from blockingStates enum>, metric2: etc.}
// const scrollbarHandleState = atom({
//   key: 'scrollbarHandleState',
//   default: null,
// });

export const currentSelectionState = atom({
  key: 'currentSelection',
  default: null,
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


const scrollbarHandleState = selector({
  key: 'scrollbarHandleState',
  get: ({get}) => {
    const maxRanges = get(maxRangesState);
    const higherIsBetter = get(higherIsBetterState);
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

const isBlockedState = selector({
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

const helpStatusState = selector({
  key: 'helpStatusState',
  get: ({get}) => {
    
    const constraints = get(constraintsState);
    const higherIsBetter = get(higherIsBetterState);
    const all = get(allCandidatesState);
    const metadata = get(metadataState);
    const selectedUid = get(currentSelectionState);
    const blocked = get(isBlockedState);

    const result = _.mapValues(constraints, (val, uid, _obj) => {
      if (!blocked) {
        return blockingStates.default;
      } 



    });
    return result;
  }
});

// // mapping from metric to the state of its handle 
// // i.e. default, blocked, blocking, bounced  
// TODO re-ithkn this, it's acting as a (possibly wrong) default
const scrollbarsState = selector({
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
});


// info from the ranges API containing
// array containing all of the candidates
// [{metric1: value1, metric2: value1}, {metric1: value3, metric2:value4}]
export const allCandidatesState = atom({  
  key: 'allCandidates', 
  default: null, 
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

export function ConstraintPane({}) {

  // name of current scenorio for url purposes e.g. "ezyfraud"
  const scenario = useRecoilValue(scenarioState);
  // largest possible ranges for specifying the scrollbar extents
  const maxRanges = useRecoilValue(maxRangesState);
  // list of currently permissible candidates based on current constraints
  const currentCandidates = useRecoilValue(currentCandidatesState);
  // the actual/current contraints as defined by the position of scrollbars
  const scrollbars = useRecoilValue(scrollbarsState);

  // current constraints done by metric
  const [_costraints, setConstraints] = useRecoilState(constraintsState);

  // all candidates sent to us by the server
  const [_allCandidates, setAllCandidates] = useRecoilState(allCandidatesState);

  // current state (e.g. blocked, bounced) of each scrollbar indexed by metric
  // const [ _bs, setBlockedScrollbar ] = useRecoilState(scrollbarHandleState);

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

  // set initial value of blockedScrollbar State
  // useEffect(() => {
  //   // TODO calculate blocking status of every scrollbar
  //   // this is really just a default that may be wrong
  //   setBlockedScrollbar(scrollbars)
  // }, [maxRanges]);

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

// function RangeConstraint({uid, min, max, marks, decimals}) {

//   const [blockedScrollbar, setBlockedScrollbar] = useRecoilState(scrollbarHandleState);
//   const [constraints, setConstraints] = useRecoilState(constraintsState);
//   const [lastBounced, setLastBounced] = useRecoilState(lastBouncedState);
//   const [targets, setTargets] = useRecoilState(targetsState);

//   const all = useRecoilValue(allCandidatesState);
//   const metricImportance = useRecoilValue(getMetricImportance);

//   const higherIsBetterMap = useRecoilValue(higherIsBetterState);
//   const higherIsBetter = higherIsBetterMap.get(uid);
//   const val = higherIsBetter ? constraints[uid][0] : constraints[uid][1];
  
//   // most desirable value in current candidate set
//   const activeOptimal = useRecoilValue(bestValuesState);
//   const activeOptimalVal = getRounded(higherIsBetterMap, uid, activeOptimal.get(uid), decimals)

//   let bounced = null;

//   enum HandleColours {
//     'white',  // default
//     'gray',   // blocked
//     'orange', // bounced
//     'red',    // blocking
//   }

//   function onChange(newVal: any) {

//     // copy constraints into a new object
//     let n = {...constraints};
    
//     // set the bounds of the scrollbar
//     n[uid] = higherIsBetter ? [newVal, n[uid][1]] : [n[uid][0], newVal];
//     const withNew = filterCandidates(all, n);

//     // TODO change to length === 0
//     if (!(withNew.length > 0)) {

//       // TODO: investigate -- this may not work -- 
//       bounced = uid;
//       setLastBounced(uid);
//       n[uid] = higherIsBetter ? [activeOptimalVal, n[uid][1]] : [n[uid][0], activeOptimalVal]; 
//     }

//     setConstraints(n);
//     changeScrollbarColours();
//   }

//   function onAfterChange() {
//     changeScrollbarColours();
//   }

//   function changeScrollbarColours() {
//     let n = {...constraints};
//     let m = {...blockedScrollbar};

//     // update the states of the scrollbar
//     const updatedLastBounce = setBlockedMetrics(n, m, uid, higherIsBetterMap, 
//       activeOptimal, bounced, lastBounced, setLastBounced, decimals, setTargets);

//     setBlockingMetrics(n, m, uid, higherIsBetterMap, activeOptimal, all, 
//       updatedLastBounce, metricImportance, setTargets, decimals);
    
//     setBlockedScrollbar(m);
//   }

//   let rangeProps = {
//     min: min,
//     max: max,
//     onChange: onChange,
//     onAfterChange: onAfterChange,
//     allowCross: false,
//     value: val,
//     step: getSliderStep(decimals),
//     handleStyle: {backgroundColor: HandleColours[blockedScrollbar[uid]], 
//       height: 17, width: 17, borderColor: HandleColours[blockedScrollbar[uid]]},
//     trackStyle: higherIsBetter ? {backgroundColor: "gray"} : {backgroundColor: "lightblue"},
//     railStyle: higherIsBetter ? {backgroundColor: "lightblue"} : {backgroundColor: "gray"},
//   };

//   if (marks !== null) {
//     rangeProps["marks"] = marks;
//     rangeProps["step"] = null;
//   }

//   // get values that would unblocking the last bounced metric and display it as text 
//   let _target = [null] 
//   if (targets != null) {
//     _target = targets[uid].map(x => getRounded(higherIsBetterMap, uid, x, decimals));
//   }

//   return (
//   <div>
//     <Slider {...rangeProps} />
//     <p>target value: {JSON.stringify(_target)}</p>
//   </div>
//   );
// }

function RangeConstraint({uid, min, max, marks, decimals}) {

  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const [currentSelection, setCurrentSelection] = useRecoilState(currentSelectionState);
  // const [lastBounced, setLastBounced] = useRecoilState(lastBouncedState);
  // const [targets, setTargets] = useRecoilState(targetsState);

  const all = useRecoilValue(allCandidatesState);
  const maxRanges = useRecoilValue(maxRangesState);
  // const metricImportance = useRecoilValue(getMetricImportance);

  const higherIsBetterMap = useRecoilValue(higherIsBetterState);
  const higherIsBetter = higherIsBetterMap[uid];
  const val = higherIsBetter ? constraints[uid][0] : constraints[uid][1];

  const isBlocked = useRecoilValue(isBlockedState);
  const blockString = (currentSelection === uid) && (isBlocked) ? "BLOCKED" : "";

  const bestCandidates = useRecoilValue(bestUnblockingCandidatesState);
  
  // most desirable value in current candidate set
  // const activeOptimal = useRecoilValue(bestValuesState);
  // const activeOptimalVal = getRounded(higherIsBetterMap, uid, activeOptimal.get(uid), decimals)

  // let bounced = null;

  enum HandleColours {
    'white',  // default
    'gray',   // blocked
    'orange', // bounced
    'red',    // blocking
  }

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

  // function onAfterChange() {
  //   changeScrollbarColours();
  // }

  // function changeScrollbarColours() {
  //   let n = {...constraints};
  //   let m = {...blockedScrollbar};

  //   // update the states of the scrollbar
  //   const updatedLastBounce = setBlockedMetrics(n, m, uid, higherIsBetterMap, 
  //     activeOptimal, bounced, lastBounced, setLastBounced, decimals, setTargets);

  //   setBlockingMetrics(n, m, uid, higherIsBetterMap, activeOptimal, all, 
  //     updatedLastBounce, metricImportance, setTargets, decimals);
    
  //   setBlockedScrollbar(m);
  // }
  
  const blockedScrollbar = useRecoilValue(scrollbarHandleState);
  const handleStyle = {
    backgroundColor: HandleColours[blockedScrollbar[uid]], 
    height: 30, 
    width: 30, 
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

  // get values that would unblocking the last bounced metric and display it as text 
  // let _target = [null] 
  // if (targets != null) {
  //   _target = targets[uid].map(x => getRounded(higherIsBetterMap, uid, x, decimals));
  // }

  return (
  <div>
    <Slider {...rangeProps} />
    <p>{"Blocked status: " + blockString}</p>
    <p>{"Best candidates: " + JSON.stringify(bestCandidates)}</p>
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
