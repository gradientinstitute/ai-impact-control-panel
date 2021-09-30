import React from 'react';


function Model(props) {
  return (
    <div>
    <Performance unit={props.unit} value={props.value} mirror={props.mirror}/>
    <ValueStatement unit={props.unit} name={props.name} 
      value={props.value} />
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

function ValueStatement(props) {
  return (
    <div>
      {props.name} {props.unit.action} {props.unit.prefix}
      {props.value.toFixed()} {props.unit.suffix}. 
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

export {Key, Model, FillBar};
