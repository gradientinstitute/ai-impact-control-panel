import { useEffect } from 'react';
import { useRecoilState, useRecoilValue } from 'recoil';
import { ArcherContainer, ArcherElement } from 'react-archer';
import _ from "lodash";
import axios from 'axios';

import { Pane, paneState, metadataState, scenarioState } from './Base';
import { algoState, nameState } from './Base';
import {sigFigs} from './Widgets';

// TODO siigh css? 
const HIGHLIGHT_COLOUR = "bg-orange-700";
const FIRST_COLOUR = "bg-gray-700";
const SECOND_COLOUR = "bg-blue-600";
const THIRD_COLOUR = "bg-green-700";


// the Introduction pane -- root node
export function IntroContext({}) {
  
  // const [metadata, setMetadata] = useRecoilState(metadataState);
  const metadata = useRecoilValue(metadataState);
  const scenario = useRecoilValue(scenarioState);
  const name = useRecoilValue(nameState);
  const algo = useRecoilValue(algoState);

  // initial request on load
  // useEffect(() => {
  //   // let req = "api/" + scenario + "/metadata";
  //   // TODO: load algo
  //   // let algo = "toy"
  //   let req = "api/" + scenario + "/init/" + algo + "/" + name;
  //   async function fetchData() {
  //     const result = await axios.get<any>(req);
  //     setMetadata(result.data);
  //   }
  //   fetchData();
  // }, []
  // );

  if (metadata === null) {
    return (<p>Loading...</p>);
  }

  return (
    <div className="mx-auto pb-8 grid gap-x-8 gap-y-6 grid-cols-1 items-center">

      <DetailBlock />

      <ObjectiveBlock
        items={metadata.objectives}
        title={"Objectives"} />

      <Pipeline />

    </div>
  );
}

function DetailBlock({}) {

  const metadata = useRecoilValue(metadataState);
  return (
    <div className="mb-8 bg-gray-700">
      <h2>SCENARIO DETAILS</h2>
      <h2 className=""> {metadata.name} </h2>
      <p className="italic">
        {metadata.purpose}
      </p>
      <p>
        <span className="font-bold">Operation:</span> {metadata.operation}
      </p>
    </div>
  );


}

// visual-ish display of the data -> model -> decision pipeline
function Pipeline({}) {

  const metadata = useRecoilValue(metadataState);

  return (
    <div className= "rounded-lg p-3 bg-gray-700 text-center">
      <h2 className="mb-3 font-bold font-xl">Pipeline</h2>

      <div className="bg-gray-600">
        <h2 className="font-bold">Data</h2>
        <p>{metadata.data}</p>
      </div>
      <div className="col-span-1">
        <BlockWithSubBlocks 
          items={metadata.targets} 
          title={"Predictions"}
          css={""}
          />
      </div>

      <div className="bg-gray-600">
        <h2 className="font-bold">Decision Rules</h2>
        <p>{metadata.decision_rules}</p>
      </div>

      <div className="col-span-1">
        <BlockWithSubBlocks
          items={metadata.actions}
          title={"Actions"}
          css={"bg-grey-800"}
          />
      </div>

    </div>
  );
}

// the metrics used to capture the objectives
// function Metrics({}) {

//   const metadata = useRecoilValue(metadataState);
//   const items = metadata.metrics;
//   const scenario = useRecoilValue(scenarioState);

//   const mapped_items = Object.entries(items).map((x) => {
//     const uid: string = x[0];
//     const data: any = x[1];
//     const capt = data.captures.join(", ");
//     const summary = data.type === "qualitative" ? <QualitativeSummary data={data} /> : <UnitRange data={data} />

//     return (
//       <div key={uid} 
//         className={SECOND_COLOUR + " grid grid-cols-1 gap-3 rounded-lg p-3"}>
//         <div className="text-left grid grid-cols-5">
//           <img className="col-span-2 row-span-2 h-20" 
//             src={"api/" + scenario + "/images/" + data.icon} />
//           <h3 className="col-span-3 font-bold">{data.name}</h3>
//           <p className="col-span-3 italic">{data.description}</p>
//         </div>
//         <SimpleBlock colour={THIRD_COLOUR} title={"Captures"} value={capt} />
//         <SimpleBlock colour={THIRD_COLOUR} title={"Limitations"} 
//           value={data.limitations} />
//         {summary}
//       </div>
//     );
//   });

//   return (
//     <div className={FIRST_COLOUR + " rounded-lg p-3"}>
//       <h3 className="text-xl font-bold">Metrics</h3>
//       <div className="grid grid-cols-3 gap-3"> 
//         {mapped_items}
//       </div>
//     </div>
//   );
// }

// function QualitativeSummary({data}) {

//   const result = data.options.map(x => (<p>{x}</p>));
  
//   return (
//     <div className={"rounded-lg p-3 items-center"}>
//       <p className="font-bold">Possible Values</p>
//       {result}
//     </div>);
// }

// // show the best case & worst case of metrics from the candidates
// function UnitRange({data}) {

//   const l = data.lowerIsBetter;
//   const sigfig = sigFigs(data);

//   const min_val = data.lowerIsBetter ? data.min.toFixed(sigfig) : data.max.toFixed(sigfig) * -1;
//   const min_str = data.prefix + min_val + " " + data.suffix;
//   const max_val = data.lowerIsBetter ? data.max.toFixed(sigfig) : data.min.toFixed(sigfig) * -1;
//   const max_str = data.prefix + max_val + " " + data.suffix;

//   const best_str = l ? min_str : max_str ;
//   const worst_str = l ? max_str : min_str;
//   const change_str = l ? "Decreases" : "Increases";

//   return (
//   <div className={"grid grid-cols-3 rounded-lg p-3 items-center"}>
//     <div className="col-span-1">
//       <p className="font-bold">Worst case</p>
//       <p>{worst_str}</p>
//     </div>
//     <div className="col-span-1">
//       <p className="italic">{change_str}</p><p> → </p>
//     </div>
//     <div className="col-span-1">
//       <p className="font-bold">Best case</p>
//       <p>{best_str}</p>
//     </div>
//   </div>);
// }

// Generic box with a title, and a named value (i.e. with units)
// function KeyValue({title, value, titleSize, valueSize, colour}) {
  
//   return (
//   <div className={colour + 
//     " grid gap-x-3 p-3 grid-cols-12 rounded-lg items-center"}>
//     <div className="col-span-3 text-center font-bold">
//       <h3 className={"" + titleSize}>{title}</h3>
//     </div>
//     <div className={"col-span-9 text-left " + valueSize}>
//       <p>{value}</p>
//     </div>
//   </div>
//   );
// }

// // Generic box with a title and a value
// function SimpleBlock({title, value, colour}) {
//   return (
//     <div className={colour + " p-3 rounded-lg"}>
//       <h2 className="font-bold">{title}</h2>
//       <p>{value}</p>
//     </div>
//   );
// }

function ObjectiveBlock({title, items}) {
  const mapped_items = Object.entries(items).map(([name, v]) => {
    return (
      <div key={name}>
        <h3 className="font-bold mb-4">{v["name"]}</h3>
        <p>{v["description"]}</p>
      </div>
    );
  });
  return (
    <div className="p-3 rounded-lg bg-gray-700">
      <h2 className="font-bold text-xl mb-3">{title}</h2>
      <div className="">
        {mapped_items}
      </div>
    </div>
  );
}

// generic block that contains multiple simplebox items
function BlockWithSubBlocks({title, items, css}) {

  const mapped_items = Object.entries(items).map(([name, d]) => {
    return (
      <div key={name} className="">
        <h3 className="font-bold">{name.replaceAll("_", " ")}</h3>
        <p>{d}</p>
      </div>
    );
  });
  return (
    <div className={"" + css}>
      <h2 className="font-bold text-xl mb-3">{title}</h2>
      <div className="">
        {mapped_items}
      </div>
    </div>
  );
}

