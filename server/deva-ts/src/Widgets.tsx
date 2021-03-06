// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>

function sigFigs(unit: any) {
    if (Number.isInteger(unit.min) && Number.isInteger(unit.max)) {
        return 0;
    }
    return 2;
}

enum rvOperations {
  'ceil',
  'floor'
}

// ceil or floor numbers to the number of decimal places specified
function roundValue(operation, number, decimals) {
  if (typeof number != "number") {
    return number;
  }  
  if (operation === rvOperations.ceil) {
    number = Math.ceil(number * (10 ** decimals)) / (10 ** decimals);
  } else if (operation === rvOperations.floor) {
    number = Math.floor(number * (10 ** decimals)) / (10 ** decimals);
  }
  return number;
}

// adjust the min and max values for higher is better
export function adjustUnitRange(unit) {
  let adjustedUnit = {}
  Object.assign(adjustedUnit, unit);

  adjustedUnit['min'] = unit['max'] * -1;
  adjustedUnit['max'] = unit['min'] * -1;
  return adjustedUnit;
}

function Model({unit, value, name, isMirror, colour="white"}) {
  const includePerformanceBar = true;
  const performanceBar = includePerformanceBar ? <Performance unit={unit} value={value} isMirror={isMirror}/> : null

  return (
    <div>
      {performanceBar}
    <ValueStatement unit={unit} name={name} 
      value={value} colour={colour}/>
    </div>
  );
}

function Key({unit}) {

  let direction = unit.lowerIsBetter === true ? "Lower" : "Higher";
  let statement = !(unit.type === "qualitative") ? <div>({direction} is better)</div> : null;

    return (
    <div className="my-auto">
      <div className="text-lg font-bold">
        {unit.name}
      </div>
        {statement}
      <div className="text-xs">
        {unit.description}
      </div>

    </div>
    );
}

function Performance({value, unit, isMirror}) {
  let p = (value - unit.min) / 
    (unit.max - unit.min) * 100;
  let lf = "min";
  let rf = "max";
  const sigfig = sigFigs(unit)
  let lv = unit.prefix + unit.min.toFixed(sigfig) 
    + unit.suffix;
  let rv = unit.prefix + unit.max.toFixed(sigfig) 
    + unit.suffix;
  if (isMirror === true) {
    lf = "max";
    rf = "min";
    lv = unit.prefix + unit.max.toFixed(sigfig) 
      + unit.suffix;
    rv = unit.prefix + unit.min.toFixed(sigfig)
      + unit.suffix;
  }

  const left = !(unit.type === "qualitative")

  ? (<div className="my-auto pr-2 text-right text-xs w-1/4">
      {lv}<br />({lf} achievable)
    </div>)

  : (<div className="my-auto pr-2 text-right text-xs w-1/4">
      {unit.options[0]}
    </div>);

const right = !(unit.type === "qualitative")

  ? <div className="my-auto text-left pl-2 text-xs w-1/4">
      {rv}<br />({rf} achievable)
    </div>

  : (<div className="my-auto text-left pl-2 text-xs w-1/4">
      {unit.options[unit.options.length - 1]}
  </div>);

  return (
    
    <div className="flex">
      {left}
      <div className="flex-grow py-3">
        <FillBar 
          unit={unit} 
          percentage={p} 
          isMirror={isMirror}
          isThin={false}
        />
      </div>
      {right}
    </div>
  );
}

function ValueStatement({name, value, unit, colour}) {
  return unit.type === "qualitative" 
    ? ValueStatementQualitative({name, value, unit, colour}) 
    : ValueStatementQuantitative({name, value, unit, colour});
}

function ValueStatementQuantitative({name, value, unit, colour}) {
  const sigfig = Number.isInteger(value) ? 0 : 2;
  return (
    <div className={"text-"+ colour}>
      {name} {unit.action} {unit.prefix}
      {value.toFixed(sigfig)}{unit.suffix}. 
    </div>
  );
}

function ValueStatementQualitative({name, value, unit, colour}) {
  return (
    <div className={"text-lg text-"+ colour}>
      {name} {unit.options[value]}. 
    </div>
  );
}

function FillBar({percentage, unit, isThin, isMirror}) {
  let lwidth = isThin === true? 2 : 4;
  let leftright = isMirror === true ? 
    " text-left ml-auto" : " text-right";
  let border = isMirror === true ? 
    "border-r-" + lwidth: "border-l-" + lwidth;
  let outer = "py-3 border-black " + border;
  let color = unit.lowerIsBetter === true ? 
    "bg-red-800" : "bg-green-700";

  return (
    <div className={outer}>
    <div className="w-full bg-gray-500">
      <div className={"h-24 min-h-full " + color + 
        " text-xs text-left text-gray-500" + leftright} 
           style={{width:percentage + "%"}}
      >
      </div>
    </div>
    </div>
  );
}

export {Key, Model, FillBar, sigFigs, roundValue, rvOperations};
