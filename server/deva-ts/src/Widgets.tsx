import React from 'react';

function sigFigs(unit) {
    if (Number.isInteger(unit.min) && Number.isInteger(unit.max)) {
        return 0;
    }
    return 2;
}

function Model({unit, value, name, isMirror}) {
  return (
    <div>
    <Performance unit={unit} value={value} isMirror={isMirror}/>
    <ValueStatement unit={unit} name={name} 
      value={value} />
    </div>
  );
}

function Key({unit}) {
  let direction = unit.higherIsBetter === true ? "Higher" : "Lower";
    return (
    <div className="my-auto">
      <div className="text-lg font-bold">
        {unit.name}
      </div>
      <div className="text-xs">
        {unit.description}
      </div>
      <div>
        ({direction} is better)
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
    + " " + unit.suffix;
  let rv = unit.prefix + unit.max.toFixed(sigfig) 
    + " " + unit.suffix;
  if (isMirror === true) {
    lf = "max";
    rf = "min";
    lv = unit.prefix + unit.max.toFixed(sigfig) 
      + " " + unit.suffix;
    rv = unit.prefix + unit.min.toFixed(sigfig)
      + " " + unit.suffix;
  }

  return (
    
    <div className="flex">
      <div className="my-auto pr-2 text-right text-xs w-1/4">{lv}<br />({lf} achievable)</div>
      <div className="flex-grow py-3">
        <FillBar 
          unit={unit} 
          percentage={p} 
          isMirror={isMirror}
          isThin={false}
        />
      </div>
      <div className="my-auto text-left pl-2 text-xs w-1/4">{rv}<br />({rf} achievable)</div>
    </div>
  );
}

function ValueStatement({name, value, unit}) {
  const sigfig = Number.isInteger(value) ? 0 : 2;
  return (
    <div>
      {name} {unit.action} {unit.prefix}
      {value.toFixed(sigfig)} {unit.suffix}. 
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
  let color = unit.higherIsBetter === true ? 
    "bg-green-700" : "bg-red-800";

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

export {Key, Model, FillBar, sigFigs};
