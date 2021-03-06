// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
import { useEffect } from 'react';
import { atom, useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil';
import axios from 'axios';
import _ from "lodash";
import {Pane, metadataState, paneState, constraintsState,
        scenarioState, nameState, algoState, configState } from './Base';
import {Key, Model, FillBar, adjustUnitRange} from './Widgets';

import {VisualiseData, radarDataState} from './RadarCharts'
import { compareConfig } from './Config';
import {HelpOverlay, overlayId, helpState} from './HelpOverlay';
import {sigFigs} from './Widgets';

const leftColour = {hex : "#93c5fd", text : "blue-300"};
const rightColour = {hex : "#fda4af", text : "pink-200"};

// the current pair of candidates sent from the server
const candidatesState = atom({
  key: 'candidates',
  default: null,
});

// the choice the user expressed by clicking (for current candidates only)
const choiceState = atom({
  key: 'choice',
  default: null,
});

// the feedback data from the user about their choice
const feedbackState = atom({
  key: 'feedback',
  default: null,
})

// main panel
export function PairwisePane() {
  
  const metadata = useRecoilValue(metadataState);
  const scenario = useRecoilValue(scenarioState);
  const name = useRecoilValue(nameState);
  const algorithm = useRecoilValue(algoState);
  const constraints = useRecoilValue(constraintsState);

  const choice = useRecoilValue(choiceState);
  const [candidates, setCandidates] = useRecoilState(candidatesState);
  const setPane = useSetRecoilState(paneState);
  const [feedback, setFeedback] = useRecoilState(feedbackState);
  const setRadarData = useSetRecoilState(radarDataState);
  const configs = useRecoilValue(configState);

  const setHelpState = useSetRecoilState(helpState);

  // initial loading of candidates
  // a bit complicated by the fact we can get either candidates or a result
  // should probably change the server interface one day
  useEffect(() => {
    const fetch = async () => {
      const payload = {
        scenario: scenario,
        algorithm: algorithm,
        constraints: constraints,
        name: name,
      }
      const result = await axios.put<any>("api/deployment/new", payload);
      const d = result.data;
      // const k = Object.keys(d);
      if (!Array.isArray(d)) {
        setPane(Pane.Result);
      } else {
        const ddash = {
          left: d[0], right: d[1]
        };
        setCandidates(ddash);
        const values = {}
        values[d[0]['name']] = d[0]['values'];
        values[d[1]['name']] = d[1]['values']; 
        setRadarData(values);
        setHelpState(overlayId.FirstOnPairwise);
      }
    }
    fetch();
  }, []
  );

  // sending new choice
  useEffect(() => {
    const send = async () => {
      let payload = {...choice};
      payload["feedback"] = feedback;
      // payload["scenario"] = scenario;
      const result = await axios.put<any>("api/deployment/choice", payload);
      const d = result.data;
      // const k = Object.keys(d);
      if (!Array.isArray(d)) {
        setPane(Pane.Result);
      } else {
        const ddash = {
          left: d[0], right: d[1]
        };
        console.log("ddsh", ddash);
        setCandidates(ddash);
        const values = {}
        values[d[0]['name']] = d[0]['values'];
        values[d[1]['name']] = d[1]['values']; 
        setRadarData(values);
      }
    }
    if (choice !== null) {
      send();
    }
  }, [choice]
  );

  // resetting user feedback
  useEffect(() => {
    const isImportant = _.mapValues(metadata.metrics, (cons, uid, _obj) => {
      return false;
      });
    const reasoningText = "";
    const feedback = {
      important: isImportant,
      reasoning: reasoningText,
    };
    setFeedback(feedback);
  }, [candidates]);

  // loading condition
  // must come after the useEffect so useEffect always runs
  if (metadata == null || candidates == null) {
    return (<h2>Loading...</h2>);
  }

  const first_uid = Object.entries(metadata.metrics)[0][0];

  function comparisons() {
    let result = []; 

    for (const [uid, u] of Object.entries(metadata.metrics)) {

      const helpFlag = (uid === first_uid);
      result.push(
      <div className="bg-gray-700 rounded-lg p-3">
        <PairwiseComparator 
          uid={uid}
          unit={u} 
          leftValue={candidates.left.values[uid]} 
          rightValue={candidates.right.values[uid]} 
          leftName={candidates.left.name} 
          rightName={candidates.right.name}
          helpFlag={helpFlag}
        />
      </div>
      );
    }
    return result;
  }

  const visualiseRadar = compareConfig(configs, 'displaySpiderPlot', 'true')
    ? <VisualiseData colour={[leftColour.hex, rightColour.hex]}/>
    : null;

  return (
    <div className="mx-auto max-w-screen-2xl grid gap-x-8 
      gap-y-6 grid-cols-1 text-center items-center">
      <div>
        <HelpOverlay hid={overlayId.FirstOnPairwise}>
        <h1 className="text-5x1 font-bold">
          Pairwise Preference Elicitation: {metadata.name}
        </h1>
        </HelpOverlay>
        <p className="italic">A system designed to {metadata.purpose}</p>
      </div>
      <HelpOverlay hid={overlayId.PairwiseRadar}>
      <div>
      {visualiseRadar}
      </div>
      </HelpOverlay>
      <InputGetter 
        leftName={candidates.left.name} 
        rightName={candidates.right.name} 
      />
      {comparisons()}
    </div>
  );
}

// Text box to fill in motivation for the choice of system
function Motivation() {
  
  const [feedback, setFeedback] = useRecoilState(feedbackState);
  const onChange = (event) => {
    const n = {
      "important": {...feedback["important"]},
      "reasoning": event.target.value
    };
    setFeedback(n);
  };

  return (
      <div>
        <p className="text-xl mb-5">What is motivating your choice? </p>

        <textarea 
          className="w-full" 
          rows={5}
          value={feedback["reasoning"]}
          onChange={onChange}
        >
        </textarea>
      </div>

  );
}

// The bottom part of the panel with the two buttons that asks for 
// users input
function InputGetter({leftName, rightName}) {
  return (
    <div className="w-auto mb-8 flex space-x-16">
      <div className="my-auto" style={{width:"5%"}}/>
      <div className="my-auto" style={{width:"20%"}}>
        <HelpOverlay hid={overlayId.PairwiseButton}>
        <div>
        <PreferenceButton 
          label={leftName} 
          me={leftName}
          other={rightName}
          color={"bg-blue-400"}
          text={"text-blue-700"}
        />
        </div>
        </HelpOverlay>
      </div>
      <HelpOverlay hid={overlayId.PairwiseText}>
      <div className="my-auto" style={{width:"50%"}}>
        <Motivation />
      </div>
      </HelpOverlay>
      <div className="my-auto" style={{width:"20%"}}>
        <PreferenceButton 
          label={rightName} 
          me={rightName}
          other={leftName}
          color={"bg-pink-200"}
          text={"text-pink-600"}
        />
      </div>
      <div className="my-auto" style={{width:"5%"}}/>
    </div>
  );
}

function PreferenceButton({me, other, label, color, text}) {

  const setChoice = useSetRecoilState(choiceState);

  function onClick() {
    setChoice({first: me, second: other});
  }

  return (
      <button className={"rounded-lg " + color} 
        onClick={onClick}>
        <div className={"p-4 text-3xl " + text}>
          I prefer {label}
        </div>
      </button>
  );
}

function FlagImportant({uid}) {
  
  const [feedback, setFeedback] = useRecoilState(feedbackState);

  const onChange = () => {
    let n = {...feedback["important"]};
    n[uid] = !n[uid];
    const result = {
      important: n,
      reasoning: feedback["reasoning"],
    }
    setFeedback(result);
  }

  return (
    <div>
      <input 
        type="checkbox" 
        name="important"  
        checked={feedback["important"][uid]}
        onChange={onChange}
      />
      <p className="text-s">Important consideration</p>
    </div>
  );
}

function PairwiseComparator({uid, leftName, leftValue, 
  rightName, rightValue, unit, helpFlag}) {

  if (!unit.lowerIsBetter) {
    unit = adjustUnitRange(unit);
    leftValue *= -1;
    rightValue *= -1;  
  }

  return (
    
    <HelpOverlay hid={helpFlag? overlayId.PairwiseDetail: -1000}>
    <div className="w-auto flex space-x-16">
      <HelpOverlay hid={helpFlag? overlayId.Important: -1000}>
      <div className="my-auto" style={{width:"10%"}}>
        <FlagImportant uid={uid} />
      </div>
      </HelpOverlay>
      <div className="my-auto" style={{width:"10%"}}>
        <Key unit={unit}/>
      </div>
      <HelpOverlay hid={helpFlag? overlayId.PairwiseAbsolute: -1000}>
      <div className="my-auto" style={{width:"30%"}}>
        <Model unit={unit} name={leftName} 
          value={leftValue} isMirror={false} colour={leftColour.text}/>
      </div>
      </HelpOverlay> 
      <HelpOverlay hid={helpFlag? overlayId.PairwiseRelative: -1000}>
      <div className="my-auto" style={{width:"20%"}}>
        {Comparison({leftValue, leftName, rightValue, rightName, unit})}
      </div>
      </HelpOverlay>
      <div className="my-auto" style={{width:"30%"}}>
        <Model unit={unit} name={rightName}
          value={rightValue} isMirror={false} colour={rightColour.text}/>
      </div>
    </div>
    </HelpOverlay>

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

function ComparisonStatementQuantitative({leftName, leftValue, 
  rightName, rightValue, unit}) {
  let delta = leftValue - rightValue;
  
  let n1 = leftName;
  let n1Colour = leftColour.text;
  let n2 = rightName;
  let n2Colour = rightColour.text;

  if (delta < 0) {
    n1 = rightName;
    n2 = leftName;
    n1Colour = rightColour.text;
    n2Colour = leftColour.text;
    delta = delta * -1;
  }
  const sigfig = sigFigs(unit)

  return (
    <div>
    <span className={"text-xl font-bold text-"+ n1Colour}>{n1 + " "}</span>
    <span className="text-xl font-bold">
      {unit.action} {unit.prefix} {delta.toFixed(sigfig)}{unit.compare}
    </span>
    <span className={"text-xl font-bold text-" + n2Colour}>{" " + n2}</span>
    <span className={"text-xl font-bold text-" + n2Colour}>.</span>
    </div>
  );
}

function ComparisonStatementQualitative({leftName, leftValue, 
  rightName, rightValue, unit}) {
  
  const n1 = leftName;
  const n2 = rightName;
  const n1Colour = leftColour.text;
  const n2Colour = rightColour.text;

  const isPreferable = (leftValue > rightValue && !unit.lowerIsBetter) || (leftValue < rightValue && unit.lowerIsBetter);
  let comparison = isPreferable ? unit.comparison_better : unit.comparison_worse;
  comparison = leftValue === rightValue ? unit.comparison_equal : comparison;

  return (
    <div>
      <span className={"text-xl font-bold text-" + n1Colour}>{n1} </span>
      <span className="text-xl font-bold">{comparison} </span>
      <span className={"text-xl font-bold text-" + n2Colour}>{n2} </span>
    </div>
  );
}

function ComparisonQuantitative({leftValue, leftName, rightValue, rightName, unit}) {
  return (
    <div>
      <DeltaBar unit={unit} leftValue={leftValue}
        rightValue={rightValue} />
      <ComparisonStatementQuantitative unit={unit} leftName={leftName}
        rightName={rightName} leftValue={leftValue} 
        rightValue={rightValue}/>
    </div>
  );
}

function ComparisonQualitative({leftValue, leftName, rightValue, rightName, unit}) {
  return (
    <div>
        <DeltaBar unit={unit} leftValue={leftValue}
        rightValue={rightValue} />
      <ComparisonStatementQualitative unit={unit} leftName={leftName}
        rightName={rightName} leftValue={leftValue} 
        rightValue={rightValue}/>
    </div>
  );
}

function Comparison({leftValue, leftName, rightValue, rightName, unit}) {

  const statement = unit.type === "qualitative" ?  ComparisonQualitative({leftValue, leftName, rightValue, rightName, unit}) :
    ComparisonQuantitative({leftValue, leftName, rightValue, rightName, unit});

  return (
    <div>
      {statement}
    </div>
  );
}
