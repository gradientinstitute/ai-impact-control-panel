import React, {useState, useEffect} from 'react';
import axios from 'axios';
import './App.css';

function App() {

  const [units, setUnits] = useState<any>(null);
  const [candidates, setCandidates] = useState<any>(null);
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

  // initial loading of candidates
  useEffect(() => {
    let req = "scenario/choice";
    async function fetchData() {
      const result = await axios.get<any>(req);
      setCandidates(result.data);
    }
    if (units != null) {
      fetchData();
    }
  }, [units]
  );
  
  let response = {
    type: "pairwise", 
    model1: {
      name: "System A",
      profit: 40, 
      fp: 320,
      }, 
    model2: {
      name: "System B", 
      profit: 50, 
      fp: 550}
  };

  function comparisons() {
    if (units == null || candidates == null) {
      return <p>Loading...</p>
    }
    let result = []; 
    for (const [uid, u] of Object.entries(units)) {
      const [name1, model1] = Object.entries(candidates)[0];
      const [name2, model2] = Object.entries(candidates)[1];
      result.push(
        <PairwiseComparator 
          unit={u} 
          leftValue={model1[uid]} 
          rightValue={model2[uid]} 
          leftName={name1} 
          rightName={name2}
        />
      );
    }
    return result;
  }


  return (
    <div className="App container mx-auto text-center">
          <h1 className="pb-8">AI Governance Control Panel</h1>
          {comparisons()}
          <InputGetter leftName={"System A"} rightName={"System B"} 
            leftF ={() => {}} rightF={() => {}}/>
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
      <button className="bg-yellow-300 rounded-lg" onClick={() => props.onClick()}>
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
  let p = (props.value - props.unit.min) / (props.unit.max - props.unit.min) * 100;
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
        <FillBar value={props.value} unit={props.unit} percentage={p} mirror={props.mirror} />
      </div>
      <div className="my-auto text-xs w-1/4">{rv}<br />({rf} acheivable)</div>
    </div>
  );
}


function FillBar(props) {
  let lwidth = props.thin === true? 2 : 4;
  let leftright = props.mirror === true ? " text-left ml-auto" : " text-right";
  let border = props.mirror === true ? "border-r-" + lwidth: "border-l-" + lwidth;
  let outer = "py-3 border-black " + border;
  let color = props.unit.higherIsBetter === true ? "bg-green-400" : "bg-red-400";

  return (
    <div className={outer}>
    <div className="w-full bg-gray-200">
      <div className={"h-24 min-h-full " + color + " text-xs text-left text-gray-500" + leftright} 
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
        <FillBar mirror={true} thin={true} unit={props.unit} value={leftValue} percentage={leftP} />
      </div>
      <div className="w-1/2 py-3">
        <FillBar mirror={false} thin={true} unit={props.unit} value={rightValue} percentage={rightP} />
      </div>
    </div>
  );
}

function ValueStatement(props) {
  return (
    <div>
      {props.name} {props.unit.action} {props.unit.prefix}{props.value} {props.unit.suffix}. 
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
      {n1} {props.unit.action} {props.unit.prefix}{delta}{props.unit.suffix} more than {n2}.
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


// https://codesandbox.io/s/jvvkoo8pq3?file=/src/index.js
// https://www.robinwieruch.de/react-hooks-fetch-data
// https://dmitripavlutin.com/react-useeffect-infinite-loop/
//function OldPairwiseComparator() {
//  const [model1, setModel1] = useState<any>(null);
//  const [model2, setModel2] = useState<any>(null);
//  const [model1Name, setModel1Name] = useState("loading");
//  const [model2Name, setModel2Name] = useState("loading");
//  const [modelChosen, setModelChosen] = useState("");
//  const [stage, setStage] = useState(1);

//  // initial request on load
//  useEffect(() => {
//    let req = "choice";
//    async function fetchData() {
//      const result = await axios.get<any>(req);
//      setModel1(result.data.model1);
//      setModel2(result.data.model2);
//    }
//    fetchData();
//    }, []
//  );

//  //Update model names on request coming back
//  useEffect(() => {
//    if (model1 !== null) {
//      setModel1Name(model1.name);
//    }
//    if (model2 !== null) {
//      setModel2Name(model2.name);
//    }
//  }, [model1, model2]);
  
//  // request on button push
//  useEffect(() => {
//    let req = "choice/" + stage + "/" + modelChosen;
//    async function fetchData() {
//      const result = await axios.get<any>(req);
//      setModel1(result.data.model1);
//      setModel2(result.data.model2);
//    }
//    if (modelChosen !== "") {
//      fetchData();
//      setModelChosen("");
//      setStage(stage => stage + 1);
//    }
//    }, [modelChosen]
//  );
  
  // return (
  //   <div className="flex flex-row gap-5">
  //     <div className="flex-1 space-y-5">
  //       <OldModelView model={model1}/>
  //       <OldButtonInterface label={model1Name} onClick = { () => { setModelChosen("1") } } />
  //     </div>
  //     <div className="flex-1 space-y-5">
  //       <OldModelView model={model2}/>
  //       <OldButtonInterface label={model2Name} onClick = { () => { setModelChosen("2") } } />
  //     </div>
  //   </div>
  // )
// }

// function OldModelView(props) {
  // return (
  //   <div className="h-48 bg-gray-50 flex flex-wrap content-center justify-center">
  //     <div>
  //     <p>I am a picture of model {JSON.stringify(props.model)}</p>
  //     </div>
  //   </div>
  //   )
// }

// function OldButtonInterface(props) {
  // return (
  //   <div>
  //     <button className="bg-green-500 rounded-lg" onClick={() => props.onClick()}>
  //       <div className="p-4">
  //         {props.label}
  //       </div>
  //     </button>
  //   </div>
  // );
// }

export default App;
