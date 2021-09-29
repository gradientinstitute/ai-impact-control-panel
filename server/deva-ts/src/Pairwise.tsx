import React, {useState, useEffect, useReducer, useContext} from 'react';
import axios from 'axios';

const ChoiceDispatch = React.createContext(null);

function choiceReducer(_state, action) {
  return action.first + "/" + action.second;
}

export function MainPane(props) {
  const metadata = props.metadata;
  const [candidates, setCandidates] = useState<any>(null);
  const [choice, dispatch] = useReducer(choiceReducer, "");
  const setResult = props.setResult;

  // loading of candidates
  useEffect(() => {
    if (metadata == null) {
      return
    }
    
    let req = choice === "" ? "choice" : "choice/" + choice;
    const fetch = async () => {
      const result = await axios.get<any>(req);
      const d = result.data;
      const k = Object.keys(d);
      if (k.length === 1) {
        setResult(d);
      } else {
        const leftName = Object.keys(d)[0];
        const rightName = Object.keys(d)[1];
        setCandidates({
          left: {name: leftName, values: d[leftName]},
          right:{name: rightName, values: d[rightName]}
        });
      }
    }
    fetch();
  }, [metadata, choice, setResult]
  );

  // loading condition
  // must come after the useEffect so useEffect always runs
  if (metadata == null || candidates == null) {
    return (<h2>Loading...</h2>);
  }

  function comparisons() {
    console.log(candidates);
    let result = []; 
    for (const [uid, u] of Object.entries(metadata.metrics)) {
      result.push(
      <div className="bg-gray-700 rounded-lg p-3">
        <PairwiseComparator 
          key={uid}
          unit={u} 
          leftValue={candidates.left.values[uid]} 
          rightValue={candidates.right.values[uid]} 
          leftName={candidates.left.name} 
          rightName={candidates.right.name}
        />
      </div>
      );
    }
    return result;
  }

    // <div className="">
  return (
    <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-6 grid-cols-1 text-center items-center">
      <div>
        <h1 className="text-5x1 font-bold">Pairwise Preference Elicitation: {metadata.name}</h1>
        <p className="italic">A system designed to {metadata.purpose}</p>
      </div>
      {comparisons()}
      <ChoiceDispatch.Provider value={dispatch}>
        <InputGetter 
          leftName={candidates.left.name} 
          rightName={candidates.right.name} 
        />
      </ChoiceDispatch.Provider>
    </div>
  );
}

function InputGetter(props) {
  return (
    <div className="w-auto mb-8 flex space-x-16">
      <div className="my-auto" style={{width:"10%"}}>
      </div>
      <div className="my-auto" style={{width:"30%"}}>
        <PreferenceButton 
          label={props.leftName} 
          me={props.leftName}
          other={props.rightName}
        />
      </div>
      <div className="my-auto" style={{width:"30%"}}>
      </div>
      <div className="my-auto" style={{width:"30%"}}>
        <PreferenceButton 
          label={props.rightName} 
          me={props.rightName}
          other={props.leftName}
        />
      </div>
    </div>
  );
}

function PreferenceButton(props) {

  const dispatch = useContext(ChoiceDispatch);
  function handleClick() {
    dispatch({ first: props.me, second: props.other });
  }

  return (
      <button className="bg-gray-200 rounded-lg" 
        onClick={handleClick}>
        <div className="p-4 text-3xl text-black">
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
      <div className="text-lg font-bold">
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
  let lv = props.unit.prefix + props.unit.min.toFixed() 
    + " " + props.unit.suffix;
  let rv = props.unit.prefix + props.unit.max.toFixed() 
    + " " + props.unit.suffix;
  if (props.mirror === true) {
    lf = "max";
    rf = "min";
    lv = props.unit.prefix + props.unit.max.toFixed() 
      + " " + props.unit.suffix;
    rv = props.unit.prefix + props.unit.min.toFixed()
      + " " + props.unit.suffix;
  }

  return (
    
    <div className="flex">
      <div className="my-auto pr-2 text-right text-xs w-1/4">{lv}<br />({lf} acheivable)</div>
      <div className="flex-grow py-3">
        <FillBar 
          value={props.value} 
          unit={props.unit} 
          percentage={p} 
          mirror={props.mirror}
        />
      </div>
      <div className="my-auto text-left pl-2 text-xs w-1/4">{rv}<br />({rf} acheivable)</div>
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
    "bg-green-700" : "bg-red-800";

  return (
    <div className={outer}>
    <div className="w-full bg-gray-500">
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
      {props.name} {props.unit.action} {props.unit.prefix}
      {props.value.toFixed()} {props.unit.suffix}. 
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
      {delta.toFixed()} {props.unit.suffix} more than {n2}.
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
