import React, {useState, useEffect, useReducer, useContext} from 'react';
import _ from "lodash";
import { ArcherContainer, ArcherElement } from 'react-archer';
import logo_FN from './FN.png';
import logo_FP from './FP.png';
import logo_FNWO from './FNWO.png';
import logo_FPWO from './FPWO.png';
import logo_profit from './profit.png';
import logo_fairness from './fairness.png';
import logo_missout from './missout.png';
import logo_shortlist from './shortlist.png';
import {SigFigs} from './Widgets';

const logos = {
  FN: logo_FN,
  FP: logo_FP,
  FNWO: logo_FNWO,
  FPWO: logo_FPWO,
  profit: logo_profit,
  fairness: logo_fairness,
  missout: logo_missout,
  shortlist: logo_shortlist,
}

const colors = {
  1: "bg-gray-700",
  2: "bg-blue-700",
  3: "bg-gray-600",
}

export function IntroPane(props) {

  const metadata = props.metadata;

  return (
    <div className="mx-auto max-w-screen-lg pb-8 grid gap-x-8 gap-y-6 grid-cols-1 text-center items-center">

      <div className="mb-8">
        <h1 className=""> System under study: {metadata.name} </h1>
        <p className="">A system {metadata.purpose}</p>
      </div>
    
      <KeyValue 
        title={"Purpose"} 
        titleSize="4xl" 
        value={metadata.operation} 
        valueSize="xl"
      />

      <ObjectiveBlock
        items={metadata.objectives}
        title={"Objectives"} />

      <Pipeline metadata={metadata} />

      <Metrics items={metadata.metrics}/>

      <ReadyButton onClick={props.onClick} />
    </div>
  );
}

function Pipeline(props) {
  const metadata = props.metadata;
  return (
    <div className="bg-gray-700 rounded-lg p-3">
    <h2 className="mb-3 font-bold font-xl">Pipeline</h2>
    <ArcherContainer strokeColor="white">
      <div className="grid grid-cols-2 gap-20 items-center">

        <ArcherElement
          id="data"
          relations={[
            {
              targetId:"predictions",
              targetAnchor: "left",
              sourceAnchor: "right",
              style: { strokeWidth: 3},
            },
          ]}
        >
          <div className="col-span-1">
            <SimpleBlock
              title={"Data"}
              value={metadata.data}
              level={2}
            />
          </div>
        </ArcherElement>


        <ArcherElement
          id="predictions"
          relations={[
            {
              targetId:"decisions",
              targetAnchor: "top",
              sourceAnchor: "bottom",
              style: { strokeWidth: 3},
            },
          ]}
        >
          <div className="col-span-1">
            <BlockWithSubBlocks 
              items={metadata.targets} 
              title={"Predictions"}
              level={2} />
          </div>
        </ArcherElement>

        <ArcherElement
          id="decisions"
          relations={[
            {
              targetId:"actions",
              targetAnchor: "left",
              sourceAnchor: "right",
              style: { strokeWidth: 3},
            },
          ]}
        >
          <div className="col-span-1">
            <SimpleBlock
              title={"Decision Rules"}
              value={metadata.decision_rules}
              level={2}
            />
          </div>
        </ArcherElement>

        <ArcherElement id="actions">
          <div className="col-span-1">
            <BlockWithSubBlocks
              items={metadata.actions}
              title={"Actions"}
              level={2} />
          </div>
        </ArcherElement>

      </div>
    </ArcherContainer>
    </div>
  );
}

function Metrics(props) {

  const color = colors[1];
  const subColor = colors[2];
  
  const items = Object.entries(props.items).map((x) => {
    const uid: string = x[0];
    const data: any = x[1];
    const capt = data.captures.join(", ");

    return (
      <div key={uid} className={subColor + " grid grid-cols-1 gap-3 rounded-lg p-3"}>
        <div className="text-left grid grid-cols-5">
          <img className="col-span-2 row-span-2 h-20" src={logos[data.icon]} />
          <h3 className="col-span-3 font-bold">{data.name}</h3>
          <p className="col-span-3 italic">{data.description}</p>
        </div>
        <SimpleBlock title={"Captures"} value={capt} level={3}/>
        <SimpleBlock title={"Limitations"} level={3} value={data.limitations} />
        <UnitRange data={data} level={3}/>
      </div>
    );
  });

  


  return (

    <div className={color + " rounded-lg p-3"}>
      <h3 className="text-xl font-bold">Metrics</h3>
      <div className="grid grid-cols-3 gap-3"> 
        {items}
      </div>
    </div>
  );
}

function UnitRange(props) {
  const level = "level" in props? props.level : 1;
  const color = colors[level];
  const data = props.data;
  const sigfig = SigFigs(data);
  const h = data.higherIsBetter;
  const min_str = data.prefix + data.min.toFixed(sigfig) + " " + data.suffix;
  const max_str = data.prefix + data.max.toFixed(sigfig) + " " + data.suffix;

  const best_str = h ? max_str : min_str;
  const worst_str = h ? min_str : max_str;
  const change_str = h ? "Increases" : "Decreases";

  return (
  <div className={color + " grid grid-cols-3 rounded-lg p-3 items-center"}>
    <div className="col-span-1">
      <p className="font-bold">Worst case</p>
      <p>{worst_str}</p>
    </div>
    <div className="col-span-1">
      <p className="italic">{change_str}</p><p> → </p>
    </div>
    <div className="col-span-1">
      <p className="font-bold">Best case</p>
      <p>{best_str}</p>
    </div>
  </div>);
}

function KeyValue(props) {
  
  const titleSize = 'titleSize' in props ? "text-" + props.titleSize : "";
  const valueSize = 'valueSize' in props ? "text-" + props.valueSize : "";
  const colorLevel = 'level' in props? props.colorLevel : 1;
  return (
  <div className={colors[colorLevel] + " grid gap-x-3 p-3 grid-cols-12 rounded-lg items-center"}>
    <div className="col-span-3 text-center font-bold">
      <h3 className={"" + titleSize}>{props.title}</h3>
    </div>
    <div className={"col-span-9 text-left " + valueSize}>
      <p>{props.value}</p>
    </div>
  </div>
  );
}

function SimpleBlock(props) {
  
  const level = "level" in props ? props.level : 1;
  const color = colors[level];
  
  return (
    <div className={color + " p-3 rounded-lg"}>
      <h2 className="font-bold">{props.title}</h2>
      <p>{props.value}</p>
    </div>
  );
}

function ObjectiveBlock(props) {

  const level = "level" in props ? props.level : 1;
  const color = colors[level];
  const subColor = colors[level + 1];
  const items = Object.entries(props.items).map(([name, v]) => {
    return (
      <div key={name} className={subColor + " p-3 rounded-lg"}>
        <h3 className="font-bold">{v["name"]}</h3>
        <p>({name})</p>
        <p>{v["description"]}</p>
      </div>
    );
  });
  return (
    <div className={color +" p-3 rounded-lg"}>
      <h2 className="font-bold text-xl mb-3">{props.title}</h2>
      <div className="flex gap-3">
        {items}
      </div>
    </div>
  );
}

function BlockWithSubBlocks(props) {

  const level = "level" in props ? props.level : 1;
  const color = colors[level];
  const subColor = colors[level + 1];
  const items = Object.entries(props.items).map(([name, d]) => {
    return (
      <div key={name} className={subColor + " p-3 rounded-lg"}>
        <h3 className="font-bold">{name.replaceAll("_", " ")}</h3>
        <p>{d}</p>
      </div>
    );
  });
  return (
    <div className={color +" p-3 rounded-lg"}>
      <h2 className="font-bold text-xl mb-3">{props.title}</h2>
      <div className="flex gap-3">
        {items}
      </div>
    </div>
  );
}

function ReadyButton(props) {
  return (
      <button className="bg-gray-200 text-black rounded-lg" 
        onClick={() => props.onClick()}>
        <div className="p-4 text-5xl">
          Begin
        </div>
      </button>
  );
}

