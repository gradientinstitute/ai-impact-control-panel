import React, {useState, useEffect, useReducer, useContext} from 'react';
import axios from 'axios';
import {Key, Model, FillBar} from './Widgets';

const ChoiceDispatch = React.createContext(null);
const sigfig = 2

function choiceReducer(_state, action) {
  return action.first + "/" + action.second;
}

export function MainPane({metadata, setResult}) {
  const [candidates, setCandidates] = useState<any>(null);
  const [choice, dispatch] = useReducer(choiceReducer, "");

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


function Motivation({}) {
  return (
    <div>
      <p className="text-xl mb-5"> What is motivating your choice? </p>
      <textarea id="reasons" className="w-full" rows={5}></textarea>
    </div>
  );
}

function InputGetter({leftName, rightName}) {
  return (
    <div className="w-auto mb-8 flex space-x-16">
      <div className="my-auto" style={{width:"10%"}}>
      </div>
      <div className="my-auto" style={{width:"20%"}}>
        <PreferenceButton 
          label={leftName} 
          me={leftName}
          other={rightName}
        />
      </div>
      <div className="my-auto" style={{width:"50%"}}>
        <Motivation />
      </div>
      <div className="my-auto" style={{width:"20%"}}>
        <PreferenceButton 
          label={rightName} 
          me={rightName}
          other={leftName}
        />
      </div>
    </div>
  );
}

function PreferenceButton({me, other, label}) {

  //TODO remove / implement, utter hack for demo
  useEffect(() => {
    const textBox: any = document.getElementById("reasons");
    textBox.value =  "";
    const checkBoxes = document.getElementsByName("important");
    for (let i=0; i < checkBoxes.length; i++) {
      checkBoxes[i]["checked"] = false;
    }

  }, [label]);

  const dispatch = useContext(ChoiceDispatch);
  function handleClick() {
    dispatch({ first: me, second: other });
  }

  return (
      <button className="bg-gray-200 rounded-lg" 
        onClick={handleClick}>
        <div className="p-4 text-3xl text-black">
          I prefer {label}
        </div>
      </button>
  );
}

function FlagImportant({}) {
  return (
    <div>
      <input type="checkbox" name="important" value="yes" />
      <p className="text-s">Important consideration</p>
    </div>
  );
}

function PairwiseComparator({leftName, leftValue, 
  rightName, rightValue, unit}) {

  return (
    
    <div className="w-auto flex space-x-16">
      <div className="my-auto" style={{width:"10%"}}>
        <FlagImportant />
      </div>
      <div className="my-auto" style={{width:"10%"}}>
        <Key unit={unit}/>
      </div>
      <div className="" style={{width:"30%"}}>
        <Model unit={unit} name={leftName} 
          value={leftValue} isMirror={false}/>
      </div>
      <div className="" style={{width:"20%"}}>
        <Comparison unit={unit} 
          leftValue={leftValue} rightValue={rightValue}
          leftName={leftName} rightName={rightName}/>
      </div>
      <div className="" style={{width:"30%"}}>
        <Model unit={unit} name={rightName}
          value={rightValue} isMirror={false}/>
      </div>
    </div>

  );
}

function DeltaBar({leftValue, rightValue, unit}) {
  
  let maxDelta = unit.max - unit.min;
  let delta = (leftValue - rightValue);
  let onLeft = delta > 0;
  let pDelta = delta / maxDelta * 100;
  let rightP = onLeft === true ? 0 : -1 * pDelta;
  let leftP = onLeft === true ? pDelta : 0;

  return (
    <div className="w-full flex">
      <div className="w-1/2 py-3">
        <FillBar 
          isMirror={true} 
          isThin={true} 
          unit={unit} 
          percentage={leftP} 
        />
      </div>
      <div className="w-1/2 py-3">
        <FillBar 
          isMirror={false} 
          isThin={true} 
          unit={unit} 
          percentage={rightP} 
        />
      </div>
    </div>
  );
}

function ComparisonStatement({leftName, leftValue, 
  rightName, rightValue, unit}) {
  let delta = leftValue - rightValue; 
  let n1 = leftName;
  let n2 = rightName;
  if (delta < 0) {
    n1 = rightName;
    n2 = leftName;
    delta = delta * -1;
  } 
  return (
    <div className="text-xl font-bold">
      {n1} {unit.action} {unit.prefix}
      {delta.toFixed(sigfig)} {unit.suffix} more than {n2}.
    </div>
);
}

function Comparison({leftValue, leftName, rightValue, rightName, unit}) {
  return (
    <div>
      <DeltaBar unit={unit} leftValue={leftValue}
        rightValue={rightValue} />
      <ComparisonStatement unit={unit} leftName={leftName}
        rightName={rightName} leftValue={leftValue} 
        rightValue={rightValue}/>
    </div>
  );
}
