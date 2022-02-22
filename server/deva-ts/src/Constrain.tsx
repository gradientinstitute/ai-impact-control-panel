import {useEffect} from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import _ from "lodash";

import { roundValue, rvOperations } from './Widgets'
import { useRecoilState, useSetRecoilState, useRecoilValue } from 'recoil';
import { metadataState, constraintsState, configState } from './Base';

import { allCandidatesState, maxRangesState, currentCandidatesState,
  filterCandidates, getSliderStep, bestValuesState, currentSelectionState, 
  blockedMetricState, isBlockedState, 
  blockedStatusState, blockingMetricsState, blockingStates, 
  unblockValuesState, blockedConstraintsState} from './ConstrainScrollbar';

import { compareConfig } from './Config';
import { radarDataState, VisualiseData } from './RadarCharts';
import {HelpOverlay, overlayRank, helpState} from './HelpOverlay';

const HandleColours = {
  0: 'white', // default
  1: 'gray',  // blocked
  2: 'red',   // blocking
  6: 'gray'  // at threshold
}

const BackgroundColours = {
  0: 'gray-700',  // default
  1: 'gray-700',  // blocked
  2: 'pink-900',  // blocking
  3: 'green-900', // resolvedBlock
  4: 'gray-700',  // currentlySelected
  5: 'blue-700',  // blockedMetric
  6: 'gray-700',  // at threshold 
}

function GetBackgroundColor(uid) {
  const blockStatus = useRecoilValue(blockedStatusState)[uid];
  return "bg-" + BackgroundColours[blockStatus];
};

function GetBorderColor(uid) {
  const blockStatus = useRecoilValue(blockedStatusState)[uid];
  return "border-" + BackgroundColours[blockStatus];
}

function GetHandleColor(uid) {
  const blockStatus = useRecoilValue(blockedStatusState)[uid];
  return HandleColours[blockStatus];
}

export function Constraints({}) {

  // largest possible ranges for specifying the scrollbar extents
  const maxRanges = useRecoilValue(maxRangesState);
  // list of currently permissible candidates based on current constraints
  const currentCandidates = useRecoilValue(currentCandidatesState);
  // the actual/current contraints as defined by the position of scrollbars

  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const setRadarData = useSetRecoilState(radarDataState);
  const configs = useRecoilValue(configState);
  const [_help, setHelpState] = useRecoilState(helpState);

  // set initial value of the constraints
  useEffect(() => {
    setConstraints(maxRanges)
  }, []);

  useEffect(() => {
    setHelpState(overlayRank.ScenarioDetails);
  }, []);

  useEffect(() => {
    const values = {}
    values["included"] = _.mapValues(maxRanges, x => x[0]);
    values["excluded"] = _.mapValues(constraints, x => x[1]);
    setRadarData(values)
  }, [constraints, maxRanges]);

  if (currentCandidates === null) {
    return (<div>Loading...</div>);
  }

  if (constraints === null) {
    return (<div>Loading...</div>);
  }

  const visualiseRadar = compareConfig(configs, 'displaySpiderPlot', 'true')
    ? (<div className=""><VisualiseData colour={["#008080", "#CC333F"]}/></div>)
    : null;

  return (
    <div className="mx-auto grid gap-4 grid-cols-1">
      <h1 className="text-left">Metric Filters</h1>
      <ConstraintStatus />
      {visualiseRadar}
      <HelpOverlay 
        rank={overlayRank.ConstraintScrollbars}
        title={"Constraints Scrollbar"} 
        msg={"This is a help messsage"} 
        placement={"top"}
      >
      <div className="mb-10">
        <MultiRangeConstraint />
      </div>
      </HelpOverlay>
    </div>
  );
}

function ConstraintStatus({}) {
  
  const curr = useRecoilValue(currentCandidatesState);
  const all = useRecoilValue(allCandidatesState);

  return (
  <div className="mb-8">
    <span className="italic text-2xl">{curr.length +" of " + all.length + " "}</span>
    candidate models remain
  </div>
  );

}

function UnitDescription({uid, unit}) {
  return (
    <div className="bg-gray-600 h-full p-4 grid grid-cols-1 gap-4">
      <h2>{unit.name}</h2>
      <p className="italic">{unit.description}</p>
      <p><span className="font-bold">Captures:</span> {unit.captures}</p>
      <p><span className="font-bold">Limitations:</span> {unit.limitations}</p>
    </div>
  )
}

function DescriptionRangeConstraint({uid, unit}) {

  const lowerIsBetter = unit.lowerIsBetter === false ? false : true;
  const maxRanges = useRecoilValue(maxRangesState);
  const constraints = useRecoilValue(constraintsState);
  const bgcolor = GetBackgroundColor(uid);

  const pane = (unit.type === "qualitative") ? 

    (<QualitativeConstraint u={unit} 
      maxRanges={maxRanges} 
      constraints={constraints}
      uid={uid}
      lowerIsBetter={lowerIsBetter}/>) :

    (<QuantitativeConstraint u={unit}
      maxRanges={maxRanges}
      constraints={constraints}
      uid={uid}
      lowerIsBetter={lowerIsBetter}/>)

  return (
    <div className={"grid grid-cols-8 " + bgcolor}>
      <div className="col-span-3">
        <UnitDescription uid={uid} unit={unit} />
      </div>
      <div className="col-span-5 my-auto">
        {pane}
      </div>
    </div>
  )


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
    return (
      <div>
        <DescriptionRangeConstraint key={uid} uid={uid} unit={u} />
      </div>
    );
  });

  return (
    <div className="grid grid-cols-1 gap-4">
      {items}
    </div>
  );
}

function QuantitativeConstraint({u, maxRanges, constraints, uid, lowerIsBetter}) {
  // TODO: remember how to specify these types in destructuring args
  const vals = maxRanges[uid];
  const sign = lowerIsBetter ? 1 : -1;
  const min = vals[0];
  const max = vals[1];
  const min_string = u.prefix + " " + (lowerIsBetter ? min : max * sign) + " " + u.suffix;
  const max_string = u.prefix + " " + (lowerIsBetter ? max : min * sign) + " " + u.suffix;
  const cmin = lowerIsBetter ? constraints[uid][0] : constraints[uid][1];
  const cmax = lowerIsBetter ? constraints[uid][1] : constraints[uid][0];
  const cstring = u.prefix + " (" + (cmin * sign) + " - " + (cmax * sign) + ")\n" + u.suffix;
  const decimals = u.displayDecimals;
  const bgcolor = GetBackgroundColor(uid);

  return (
    <div key={uid} 
    className={"grid grid-cols-5 gap-8 p-4 " + bgcolor}>
      
      <p className="col-span-5 text-xl text-center">{cstring}</p>

      <p className="col-span-1 text-xs text-right my-auto">{min_string}</p>
      <div className="col-span-3 my-auto">
        <RangeConstraint uid={uid} min={min} max={max} marks={null} decimals={decimals} lowerIsBetter={lowerIsBetter}/>
      </div>
      <p className="col-span-1 text-xs text-left my-auto">{max_string}</p>
    </div>
  )
}

function QualitativeConstraint({u, maxRanges, constraints, uid, lowerIsBetter}) {
  const vals = maxRanges[uid];
  const min = vals[0];
  const max = vals[1];
  const cmin = constraints[uid][0];
  const cmax = constraints[uid][1];
  const bgcolor = GetBackgroundColor(uid);
  const options = (u.options).slice(min, max + 1);

  const markstyle = {
    color: "white"
  }

  const marks = Object.fromEntries(
    options.map(x => [u.options.indexOf(x), { label: x, style: markstyle }])
  )

  return (
    <div key={uid} className={"py-15 px-20 " + bgcolor}>
        <RangeConstraint uid={uid} min={min} max={max} marks={marks} decimals={null} lowerIsBetter={lowerIsBetter}/>
    </div>
  )
}

function RangeConstraint({uid, min, max, marks, decimals, lowerIsBetter}) {

  const [constraints, setConstraints] = useRecoilState(constraintsState);
  const [currentSelection, setCurrentSelection] = useRecoilState(currentSelectionState);
  const [blockedMetric, setBlockedMetric] = useRecoilState(blockedMetricState);

  const all = useRecoilValue(allCandidatesState);
  const thresholdValues = useRecoilValue(bestValuesState);
  const val = constraints[uid][1];

  const isBlocked = useRecoilValue(isBlockedState);

  function onBeforeChange() {
    setCurrentSelection(uid);
  };

  function onChange(newVal: any) {

    // copy constraints into a new object
    let n = {...constraints};

    // set the bounds of the scrollbar
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
  
  const handleStyle = {
    backgroundColor: GetHandleColor(uid), 
    height: 20, 
    width: 20, 
    borderColor: GetHandleColor(uid)
  };

  let rangeProps = {
    min: min,
    max: max,
    onBeforeChange: onBeforeChange,
    onChange: onChange,
    allowCross: false,
    value: val,
    step: getSliderStep(decimals),
    handleStyle: handleStyle, 
    trackStyle: {backgroundColor: "lightblue"},
    railStyle: {backgroundColor: "gray"},
    reverse: !lowerIsBetter,
  };
  
  // for qualitative metrics
  if (marks !== null) {
    rangeProps["marks"] = marks;
    rangeProps["step"] = null;
  }

  const blockedStatus = useRecoilValue(blockedStatusState)[uid];
  const minPercentage = GetTargetMinPercentages(uid, min, max, decimals, lowerIsBetter);
  const maxPercentage = GetTargetMaxPercentages(uid, min, max, decimals, lowerIsBetter);

  const buttonEnabled = (blockedMetric === uid) 
    || (blockedMetric === null && currentSelection === uid && isBlocked)

  const button = buttonEnabled 
    ? <UnblockButton uid={uid} buttonDisabled={!buttonEnabled}/> 
    : <StatusButton uid={uid}/>

  return (
  <div>
    <BlockingTargetBar uid={uid} minPercentage={minPercentage} maxPercentage={maxPercentage}
      blockedStatus={blockedStatus} lowerIsBetter={lowerIsBetter}/>
    <Slider {...rangeProps} />
    <OptimalDirection lowerIsBetter={lowerIsBetter}/>
    <div className="text-center">
      {button}
    </div>
  </div>
  );
}

function StatusButton({uid}) {

  const StatusText = {
    0: 'Default',        // default
    1: 'Blocked',        // overridden by toggle button (blockedMetric)
    2: 'Blocking',       //
    3: 'Resolved Block', // overridden by toggle button 
    4: 'Selected',       // currently selected
    5: 'Blocked',        //
    6: 'At Threshold',   // 
  }

  const blockStatus = useRecoilValue(blockedStatusState)[uid];
  const bgcolor = GetBackgroundColor(uid);
  const text = StatusText[blockStatus];
  const visibility = ["Default", "Selected"].includes(text) ? " invisible" : "";

  return (
    <button className={bgcolor + "text-xl uppercase py-2 px-8 font-bold rounded-lg" + visibility}
      onMouseOver={() => {
        // TODO: display information to guide user 
        console.log("HOVERING OVER BUTTON");
      }}
    >
    {text}
    </button>
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

function GetTargetMinPercentages(uid, min, max, decimals, lowerIsBetter) {
  const blockingMetrics = useRecoilValue(blockingMetricsState).blockingMetrics;
  let percentages = [];
  if (blockingMetrics.has(uid)) {
    percentages = ([...blockingMetrics.get(uid)])
      .map(x => x.targetValue)
      .map(x => ((x - min) / (max - min)) * 100)
      .map(x => lowerIsBetter ? x : 100 - x);
  }
  return lowerIsBetter ? Math.min(...percentages) : Math.max(...percentages);
}

function GetTargetMaxPercentages(uid, min, max, decimals, lowerIsBetter) {
  const unblockValues = useRecoilValue(unblockValuesState);
  let percentage = null;
  if (unblockValues.get(uid) != 'undefined') {
    percentage = ((unblockValues.get(uid) - min) / (max - min)) * 100;
    percentage = lowerIsBetter ? percentage : 100 - percentage;
  }
  return percentage;
}

function BlockingTargetBar({uid, minPercentage, maxPercentage, blockedStatus, lowerIsBetter}) {

  // determine whether or not the target line is visible
  const isBlocking = blockedStatus === blockingStates.blocking;
  const borderColour = isBlocking ? "border-yellow-500" : GetBorderColor(uid);
  const borderColourUnblock = isBlocking ? "border-green-500" : GetBorderColor(uid);
  
  let bgColourDefault = isBlocking ? "bg-gray-600" : GetBackgroundColor(uid);
  let bgColour = isBlocking ? "bg-yellow-500" : GetBackgroundColor(uid);
  let bgColourUnblock = isBlocking ? "bg-green-500" : GetBackgroundColor(uid);

  const lowerIsBetterTarget = (
    <div className="w-full flex">
      <div className={"h-6 min-h-full " + bgColourDefault + " " + borderColour} 
        style={{width:minPercentage + "%"}}> 
      </div>
      <div className={"h-6 min-h-full border-r-4 " + bgColour + " " + borderColourUnblock} 
        style={{width:(maxPercentage - minPercentage) + "%"}}> 
      </div>
      <div className={"h-6 min-h-full " + bgColourUnblock} 
        style={{width:(100-maxPercentage) + "%"}}> 
      </div>
    </div>
  );

  const higherIsBetterTarget = (
    <div className="w-full flex">
      <div className={"h-6 min-h-full " + bgColourUnblock + " " + borderColourUnblock} 
        style={{width:maxPercentage + "%"}}> 
      </div>
      <div className={"h-6 min-h-full border-l-4 " + bgColour + " " + borderColourUnblock} 
        style={{width:(minPercentage - maxPercentage) + "%"}}> 
      </div>
      <div className={"h-6 min-h-full " + bgColourDefault} 
        style={{width:(100-minPercentage) + "%"}}> 
      </div>
    </div>
  );

  return lowerIsBetter ? lowerIsBetterTarget : higherIsBetterTarget;
}

function UnblockButton({uid, buttonDisabled}) {

  const [blockedMetric, setBlockedMetric] = useRecoilState(blockedMetricState);
  const [_blockedConstraints, setBlockedConstraints] = useRecoilState(blockedConstraintsState);
  const currentConstraints = useRecoilValue(constraintsState);

  const text = (blockedMetric === uid) 
    ? "finish unblocking"
    : "suggest metrics to unblock";

  return (
    <button className="btn text-l text-white uppercase py-2 px-6 font-bold rounded-lg"
      onClick={() => {
        if (blockedMetric === uid) {
          setBlockedMetric(null);
          setBlockedConstraints(null);
        } else {
          setBlockedMetric(uid);
          setBlockedConstraints(currentConstraints);
        }
      }}
      disabled={buttonDisabled}>
      {text}
    </button>
  );
}

