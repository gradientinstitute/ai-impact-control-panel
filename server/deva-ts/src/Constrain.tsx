import {useState, useEffect} from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { atom, selector, useRecoilState, useRecoilValue } from 'recoil';
import {Pane, paneState, scenarioState, 
        metadataState, constraintsState } from './Base';
import axios from 'axios';
import _, { indexOf, last } from "lodash";
import {roundValue, rvOperations} from './Widgets';
import {getMetricImportance, lastBouncedState, scrollbarHandleState, 
        setBlockedMetrics, setBlockingMetrics, scrollbarsState, 
        bestValuesState} from './ConstrainScrollbar';

export const allCandidatesState = atom({  
  key: 'allCandidates', 
  default: null, 
});

// maximum possible ranges (doesnt change)
export const maxRangesState = selector({
  key: 'maxRanges',
  get: ({get}) => {
    const all = get(allCandidatesState);
    const metadata = get(metadataState);

    if (all === null) {
      return null;
    }
    
    const ranges = _.mapValues(metadata.metrics, (val, uid, _obj) => {
      const decimals = 'decimals' in val ? val.decimals : 0; 
      const tvals = all.map(x => x[uid]);
      const min = roundValue(rvOperations.floor, Math.min(...tvals), decimals); 
      const max = roundValue(rvOperations.ceil, Math.max(...tvals), decimals); 
      return [min, max];
    });
    return ranges;
  },
});

// higher is better map (doesnt change)
export const higherIsBetterState = selector({
  key: 'higherIsBetter',
  get: ({get}) => {
    const metadata = get(metadataState);
    let higherIsBetterMap = new Map();
    Object.entries(metadata.metrics).map((x) => {
      const uid = x[0];
      const u: any = x[1];
      higherIsBetterMap.set(uid, u.higherIsBetter);
    });
    return higherIsBetterMap;
  }
})

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

  const scenario = useRecoilValue(scenarioState);
  const maxRanges = useRecoilValue(maxRangesState);
  const curr = useRecoilValue(currentCandidatesState);
  const scrollbars = useRecoilValue(scrollbarsState);

  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const [allCandidates, setAllCandidates] = useRecoilState(allCandidatesState);
  const [blockedScrollbar, setBlockedScrollbar] = useRecoilState(scrollbarHandleState);

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

  // set initial value of the constraints
  useEffect(() => {
    setBlockedScrollbar(scrollbars)
  }, [scrollbars]);

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

  return (
    <div key={uid} className="grid grid-cols-5 gap-8 bg-gray-600 rounded-lg p-4">
      
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
    <div key={uid} className="grid grid-cols-10 gap-8 bg-gray-600 rounded-lg p-4">
            
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

function getSliderStep(max, min, decimals) {
  if (decimals == null) { 
    return 1;
  }
  return Number((0.1 ** decimals).toFixed(decimals));
}

function RangeConstraint({uid, min, max, marks, decimals}) {

  const [blockedScrollbar, setBlockedScrollbar] = useRecoilState(scrollbarHandleState);
  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const [lastBounced, setLastBounced] = useRecoilState(lastBouncedState);

  const all = useRecoilValue(allCandidatesState);
  const activeOptimal = useRecoilValue(bestValuesState);
  const metricImportance = useRecoilValue(getMetricImportance);

  const higherIsBetterMap = useRecoilValue(higherIsBetterState);
  const higherIsBetter = higherIsBetterMap.get(uid);
  const val = higherIsBetter ? constraints[uid][0] : constraints[uid][1];
  
  let bounced = null;

  enum HandleColours {
    'white',  // default
    'gray',   // blocked
    'orange', // bounced
    'red',    // blocking
  }

  function onChange(newVal: any) {
    let n = {...constraints};
    let m = {...blockedScrollbar};

    // set the bounds of the scrollbar
    n[uid] = higherIsBetter ? [newVal, n[uid][1]] : [n[uid][0], newVal];
    const withNew = filterCandidates(all, n);

    if (withNew.length > 0) {
      setConstraints(n);
    } else {
      bounced = uid;
      setLastBounced(uid);
    }

    // change scrollbar handle colours
    changeScrollbarColours();
    setBlockedScrollbar(m);
  }

  function onAfterChange() {
    changeScrollbarColours();
  }

  function changeScrollbarColours() {
    let n = {...constraints}
    let m = {...blockedScrollbar};
    const b = setBlockedMetrics(n, m, higherIsBetterMap, activeOptimal, uid, 
      bounced, lastBounced, setLastBounced, decimals);
    setBlockingMetrics(n, m, uid, higherIsBetterMap, activeOptimal, all, b, metricImportance);
    setBlockedScrollbar(m);
  }

  let rangeProps = {
    min: min,
    max: max,
    onChange: onChange,
    onAfterChange: onAfterChange,
    allowCross: false,
    value: val,
    step: getSliderStep(max, min, decimals),
    handleStyle: {backgroundColor: HandleColours[blockedScrollbar[uid]], height: 17, width: 17, borderColor: HandleColours[blockedScrollbar[uid]]},
    trackStyle: higherIsBetter ? {backgroundColor: "gray"} : {backgroundColor: "lightblue"},
    railStyle: higherIsBetter ? {backgroundColor: "lightblue"} : {backgroundColor: "gray"},
  };

  if (marks !== null) {
    rangeProps["marks"] = marks;
    rangeProps["step"] = null;
  }

  return (
  <div>
    <Slider {...rangeProps} />
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
