import { useEffect } from 'react';
import { useRecoilState, useRecoilValue } from 'recoil';
import { ArcherContainer, ArcherElement } from 'react-archer';
import _ from "lodash";
import axios from 'axios';

import { Pane, paneState, metadataState, scenarioState } from './Base';
import {sigFigs} from './Widgets';

// TODO siigh css? 
const HIGHLIGHT_COLOUR = "bg-orange-700";
const FIRST_COLOUR = "bg-gray-700";
const SECOND_COLOUR = "bg-blue-600";
const THIRD_COLOUR = "bg-green-700";


// the Introduction pane -- root node
export function IntroPane({}) {
  
  const [metadata, setMetadata] = useRecoilState(metadataState);
  const scenario = useRecoilValue(scenarioState);

  // initial request on load
  useEffect(() => {
    let req = scenario + "/metadata";
    async function fetchData() {
      const result = await axios.get<any>(req);
      setMetadata(result.data);
    }
    fetchData();
  }, []
  );

  if (metadata === null) {
    return (<p>Loading...</p>);
  }

  return (
    <div className="mx-auto max-w-screen-lg pb-8 grid gap-x-8 
      gap-y-6 grid-cols-1 text-center items-center">

      <div className="mb-8">
        <h1 className=""> System under study: {metadata.name} </h1>
        <p className="">A system {metadata.purpose}</p>
      </div>
    
      <KeyValue 
        title={"Purpose"} 
        titleSize="4xl" 
        value={metadata.operation} 
        valueSize="xl"
        colour={HIGHLIGHT_COLOUR}
      />

      <ObjectiveBlock
        items={metadata.objectives}
        title={"Objectives"} />

      <Pipeline />

      <Metrics />

      <ReadyButton />
    </div>
  );
}

// visual-ish display of the data -> model -> decision pipeline
function Pipeline({}) {

  const metadata = useRecoilValue(metadataState);

  return (
    <div className= {FIRST_COLOUR + " rounded-lg p-3"}>
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
                colour={SECOND_COLOUR}
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
                />
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
                colour={SECOND_COLOUR}
              />
            </div>
          </ArcherElement>

          <ArcherElement id="actions">
            <div className="col-span-1">
              <BlockWithSubBlocks
                items={metadata.actions}
                title={"Actions"}
                />
            </div>
          </ArcherElement>

        </div>
      </ArcherContainer>
    </div>
  );
}

// the metrics used to capture the objectives
function Metrics({}) {

  const metadata = useRecoilValue(metadataState);
  const items = metadata.metrics;
  const scenario = useRecoilValue(scenarioState);

  const mapped_items = Object.entries(items).map((x) => {
    const uid: string = x[0];
    const data: any = x[1];
    const capt = data.captures.join(", ");

    return (
      <div key={uid} 
        className={SECOND_COLOUR + " grid grid-cols-1 gap-3 rounded-lg p-3"}>
        <div className="text-left grid grid-cols-5">
          <img className="col-span-2 row-span-2 h-20" 
            src={scenario + "/images/" + data.icon} />
          <h3 className="col-span-3 font-bold">{data.name}</h3>
          <p className="col-span-3 italic">{data.description}</p>
        </div>
        <SimpleBlock colour={THIRD_COLOUR} title={"Captures"} value={capt} />
        <SimpleBlock colour={THIRD_COLOUR} title={"Limitations"} 
          value={data.limitations} />
        <UnitRange data={data} />
      </div>
    );
  });

  return (
    <div className={FIRST_COLOUR + " rounded-lg p-3"}>
      <h3 className="text-xl font-bold">Metrics</h3>
      <div className="grid grid-cols-3 gap-3"> 
        {mapped_items}
      </div>
    </div>
  );
}

// show the best case & worst case of metrics from the candidates
function UnitRange({data}) {

  const sigfig = sigFigs(data);
  const h = data.higherIsBetter;
  const min_str = data.prefix + data.min.toFixed(sigfig) + " " + data.suffix;
  const max_str = data.prefix + data.max.toFixed(sigfig) + " " + data.suffix;

  const best_str = h ? max_str : min_str;
  const worst_str = h ? min_str : max_str;
  const change_str = h ? "Increases" : "Decreases";

  return (
  <div className={"grid grid-cols-3 rounded-lg p-3 items-center"}>
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

// Generic box with a title, and a named value (i.e. with units)
function KeyValue({title, value, titleSize, valueSize, colour}) {
  
  return (
  <div className={colour + 
    " grid gap-x-3 p-3 grid-cols-12 rounded-lg items-center"}>
    <div className="col-span-3 text-center font-bold">
      <h3 className={"" + titleSize}>{title}</h3>
    </div>
    <div className={"col-span-9 text-left " + valueSize}>
      <p>{value}</p>
    </div>
  </div>
  );
}

// Generic box with a title and a value
function SimpleBlock({title, value, colour}) {
  return (
    <div className={colour + " p-3 rounded-lg"}>
      <h2 className="font-bold">{title}</h2>
      <p>{value}</p>
    </div>
  );
}

function ObjectiveBlock({title, items}) {
  const mapped_items = Object.entries(items).map(([name, v]) => {
    return (
      <div key={name} className={SECOND_COLOUR + " p-3 rounded-lg"}>
        <h3 className="font-bold mb-4">{v["name"]}</h3>
        <p>{v["description"]}</p>
      </div>
    );
  });
  return (
    <div className={FIRST_COLOUR + " p-3 rounded-lg"}>
      <h2 className="font-bold text-xl mb-3">{title}</h2>
      <div className="flex gap-3">
        {mapped_items}
      </div>
    </div>
  );
}

// generic block that contains multiple simplebox items
function BlockWithSubBlocks({title, items}) {

  const mapped_items = Object.entries(items).map(([name, d]) => {
    return (
      <div key={name} className={THIRD_COLOUR + " p-3 rounded-lg"}>
        <h3 className="font-bold">{name.replaceAll("_", " ")}</h3>
        <p>{d}</p>
      </div>
    );
  });
  return (
    <div className={SECOND_COLOUR + " p-3 rounded-lg"}>
      <h2 className="font-bold text-xl mb-3">{title}</h2>
      <div className="flex gap-3">
        {mapped_items}
      </div>
    </div>
  );
}

// button to proceed to the next pane
function ReadyButton({}) {
  const [_pane, setPane] = useRecoilState(paneState);
  return (
      <button className="bg-gray-200 text-black rounded-lg" 
        onClick={() => {setPane(Pane.Constrain)}}>
        <div className="p-4 text-5xl">
          Begin
        </div>
      </button>
  );
}

