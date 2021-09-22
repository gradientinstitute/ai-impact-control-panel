import React, {useState, useEffect} from 'react';
import axios from 'axios';
import './App.css';

// References for fetching from server
// https://codesandbox.io/s/jvvkoo8pq3?file=/src/index.js
// https://www.robinwieruch.de/react-hooks-fetch-data
// https://dmitripavlutin.com/react-useeffect-infinite-loop/
function App() {
  return (
    <div className="App container mx-auto text-center">
      <h1 className="pb-8">AI Governance Control Panel</h1>
      <MainPane />
    </div>
  );
}


function MainPane() {

  const [units, setUnits] = useState<any>(null);
  const [candidates, setCandidates] = useState<any>(null);
  const [choice, setChoice] = useState<string>("");

  // initial request on load
  useEffect(() => {
    let req = "scenario";
    async function fetchData() {
      const result = await axios.get<any>(req);
      setUnits(result.data);
    }
    fetchData();
  }, []
  );

  async function fetchCandidates(req: string) {
    const result = await axios.get<any>(req);
    const d = result.data;
    const leftName = Object.keys(d)[0];
    const rightName = Object.keys(d)[1];
    setCandidates({
        left: {name: leftName, values: d[leftName]},
        right:{name: rightName, values: d[rightName]}
    });
  }

  // initial loading of candidates
  useEffect(() => {
    if (units != null) {
      let req = "scenario/choice";
      fetchCandidates(req);
    }
  }, [units]
  );

  // request on button push
  useEffect(() => {
    if (choice !== "") {
      let req = "scenario/choice/" + choice;
      fetchCandidates(req);
      setChoice("");
    }}, [choice]);

  // loading condition
  if (units == null || candidates == null) {
    return (<h2>Loading...</h2>);
  }

  function comparisons() {
    console.log(candidates);
    let result = []; 
    for (const [uid, u] of Object.entries(units)) {
      result.push(
        <PairwiseComparator 
          key={uid}
          unit={u} 
          leftValue={candidates.left.values[uid]} 
          rightValue={candidates.right.values[uid]} 
          leftName={candidates.left.name} 
          rightName={candidates.right.name}
        />
      );
    }
    return result;
  }


  return (
    <div className="">
      {comparisons()}
      <InputGetter 
        leftName={candidates.left.name} 
        rightName={candidates.right.name} 
        leftF ={() => {setChoice(candidates.left.name)}} 
        rightF={() => {setChoice(candidates.right.name)}}
      />
    </div>
  );
}

function InputGetter(props) {
  return (
    <div className="w-auto mt-16 flex space-x-16">
      <div className="my-auto" style={{width:"10%"}}>
      </div>
      <div className="my-auto" style={{width:"30%"}}>
        <PreferenceButton onClick={props.leftF} label={props.leftName} />
      </div>
      <div className="my-auto" style={{width:"30%"}}>
      </div>
      <div className="my-auto" style={{width:"30%"}}>
        <PreferenceButton onClick={props.rightF} label={props.rightName} />
      </div>
    </div>
  );
}

function PreferenceButton(props) {
  return (
      <button className="bg-yellow-300 rounded-lg" 
        onClick={() => props.onClick()}>
        <div className="p-4">
          I prefer {props.label}
        </div>
      </button>
  );
}

function PairwiseComparator(props) {

  return (
    
    <div className="w-auto flex space-x-16">
      <div className="my-auto" style={{width:"10%"}}>
        <Key unit={props.unit}/>
      </div>
      <div className="" style={{width:"30%"}}>
        <Model unit={props.unit} name={props.leftName} 
          value={props.leftValue} mirror={false}/>
      </div>
      <div className="" style={{width:"30%"}}>
        <Comparison unit={props.unit} 
          leftValue={props.leftValue} rightValue={props.rightValue}
          leftName={props.leftName} rightName={props.rightName}/>
      </div>
      <div className="" style={{width:"30%"}}>
        <Model unit={props.unit} name={props.rightName}
          value={props.rightValue} mirror={true}/>
      </div>
    </div>

  );
}

function Key(props) {
  let direction = props.unit.higherIsBetter === true ? "Higher" : "Lower";
    return (
    <div className="my-auto">
      <div>
        {props.unit.name}
      </div>
      <div className="text-xs">
        {props.unit.description}
      </div>
      <div>
        ({direction} is better)
      </div>
    </div>
    );
}

function Performance(props) {
  let p = (props.value - props.unit.min) / 
    (props.unit.max - props.unit.min) * 100;
  let lf = "min";
  let rf = "max";
  let lv = props.unit.prefix + props.unit.min + props.unit.suffix;
  let rv = props.unit.prefix + props.unit.max + props.unit.suffix;
  if (props.mirror === true) {
    lf = "max";
    rf = "min";
    lv = props.unit.prefix + props.unit.max + props.unit.suffix;
    rv = props.unit.prefix + props.unit.min + props.unit.suffix;
  }

  return (
    
    <div className="flex">
      <div className="my-auto text-xs w-1/4">{lv}<br />({lf} acheivable)</div>
      <div className="flex-grow py-3">
        <FillBar 
          value={props.value} 
          unit={props.unit} 
          percentage={p} 
          mirror={props.mirror}
        />
      </div>
      <div className="my-auto text-xs w-1/4">{rv}<br />({rf} acheivable)</div>
    </div>
  );
}


function FillBar(props) {
  let lwidth = props.thin === true? 2 : 4;
  let leftright = props.mirror === true ? 
    " text-left ml-auto" : " text-right";
  let border = props.mirror === true ? 
    "border-r-" + lwidth: "border-l-" + lwidth;
  let outer = "py-3 border-black " + border;
  let color = props.unit.higherIsBetter === true ? 
    "bg-green-400" : "bg-red-400";

  return (
    <div className={outer}>
    <div className="w-full bg-gray-200">
      <div className={"h-24 min-h-full " + color + 
        " text-xs text-left text-gray-500" + leftright} 
           style={{width:props.percentage + "%"}}
      >
      </div>
    </div>
    </div>
  );
}

function DeltaBar(props) {
  
  let maxDelta = props.unit.max - props.unit.min;
  let delta = (props.leftValue - props.rightValue);
  let onLeft = delta > 0;
  let pDelta = delta / maxDelta * 100;
  let leftValue = onLeft === true ? delta : "";
  let rightValue = onLeft === true ? "" : -1 * delta;
  let rightP = onLeft === true ? 0 : -1 * pDelta;
  let leftP = onLeft === true ? pDelta : 0;

  return (
    <div className="w-full flex">
      <div className="w-1/2 py-3">
        <FillBar 
          mirror={true} 
          thin={true} 
          unit={props.unit} 
          value={leftValue} 
          percentage={leftP} 
        />
      </div>
      <div className="w-1/2 py-3">
        <FillBar 
          mirror={false} 
          thin={true} 
          unit={props.unit} 
          value={rightValue} 
          percentage={rightP} 
        />
      </div>
    </div>
  );
}

function ValueStatement(props) {
  return (
    <div>
      {props.name} {props.unit.action} {props.unit.prefix}{props.value}
      {props.unit.suffix}. 
    </div>
);
}

function ComparisonStatement(props) {
  let delta = props.leftValue - props.rightValue; 
  let n1 = props.leftName;
  let n2 = props.rightName;
  if (delta < 0) {
    n1 = props.rightName;
    n2 = props.leftName;
    delta = delta * -1;
  } 
  return (
    <div className="text-xl font-bold">
      {n1} {props.unit.action} {props.unit.prefix}
      {delta}{props.unit.suffix} more than {n2}.
    </div>
);
}

function Model(props) {
  return (
    <div>
    <Performance unit={props.unit} value={props.value} mirror={props.mirror}/>
    <ValueStatement unit={props.unit} name={props.name} 
      value={props.value} />
    </div>
  );
}

function Comparison(props) {
  return (
    <div>
      <DeltaBar unit={props.unit} leftValue={props.leftValue}
        rightValue={props.rightValue} />
      <ComparisonStatement unit={props.unit} leftName={props.leftName}
        rightName={props.rightName} leftValue={props.leftValue} 
        rightValue={props.rightValue}/>
    </div>
  );
}

export default App;
