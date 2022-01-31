import { useEffect } from 'react';
import { atom, useRecoilState, useRecoilValue } from 'recoil';
import { ArcherContainer, ArcherElement } from 'react-archer';
import _ from "lodash";
import axios from 'axios';

import { Pane, paneState, algoState, nameState, 
         metadataState, scenarioState} from './Base';
import {sigFigs} from './Widgets';

// TODO siigh css? 
const HIGHLIGHT_COLOUR = "bg-orange-700";
const FIRST_COLOUR = "bg-gray-700";
const SECOND_COLOUR = "bg-blue-600";
const THIRD_COLOUR = "bg-green-700";

// the set of algorithms retrieved from the serever
const algoChoicesState = atom({
    key: 'algorithmChoices',
    default: [],
  });

// info from the ranges API containing
// array containing all of the candidates
// [{metric1: value1, metric2: value1}, {metric1: value3, metric2:value4}]
export const allCandidatesState = atom({  
  key: 'allCandidates', 
  default: null, 
});

// root node
export function ConfigurePane({}) {
  
  const scenario = useRecoilValue(scenarioState);

  // const name = useRecoilValue(nameState);
  // algorithms / eliciters
  // const algo = useRecoilValue(algoState);
  
  // all candidates sent to us by the server
  const [_current, setCurrent] = useRecoilState(algoState);
  const [metadata, setMetadata] = useRecoilState(metadataState);
  const [algorithms, setAlgos] = useRecoilState(algoChoicesState);
  const [_allCandidates, setAllCandidates] = useRecoilState(allCandidatesState);


  // initial request on load
  useEffect(() => {
    let req = "api/" + scenario + "/all";
    async function fetchData() {
      const result = await axios.get<any>(req);
      const d = result.data;
      setMetadata(d.metadata);
      setAlgos(d.algorithms);
      setAllCandidates(d.candidates);
      // setBaselines(d.baselines);
    }
    fetchData();
  }, []
  );
  
  // default selection of a particular algorithm
  useEffect( () => {
    if (algorithms !== null) {
      setCurrent(Object.keys(algorithms)[0]);
    }
  }, [algorithms]);

  // if (metadata === null) {
  //   return (<p>Loading...</p>);
  // }

  return (
    <div>
      <p>Metadata: {JSON.stringify(metadata)}</p>
    </div>
  );

  // return (
  //   <div className="mx-auto max-w-screen-lg pb-8 grid gap-x-8 
  //     gap-y-6 grid-cols-1 text-center items-center">

  //     <div className="mb-8">
  //       <h1 className=""> System under study: {metadata.name} </h1>
  //       <p className="">A system {metadata.purpose}</p>
  //     </div>
    
  //     <KeyValue 
  //       title={"Purpose"} 
  //       titleSize="4xl" 
  //       value={metadata.operation} 
  //       valueSize="xl"
  //       colour={HIGHLIGHT_COLOUR}
  //     />

  //     <ObjectiveBlock
  //       items={metadata.objectives}
  //       title={"Objectives"} />

  //     <Pipeline />

  //     <Metrics />

  //     <ReadyButton />
  //   </div>
  // );
}

// Select algorithm from list and preview details
function AlgoSelector({}) {
  
  const algos = useRecoilValue(algoChoicesState);
  const [current, setCurrent] = useRecoilState(algoState);

  const elements = Object.entries(algos).map(([name, d]) => {
    return (<option key={name} value={name}>{name}</option>);
  });
  
  return (
      <div className="p-4 gap-4 bg-gray-500 grid grid-cols-3" >
        <p className="text-right col-span-1">Eliciter</p>
        <select className="col-span-2" name="scenarios" value={current} 
          onChange={ (x) => {setCurrent(x.target.value)}}>
          {elements}
        </select>
        <div className="col-span-1">
        </div>
        <div className="col-span-2">
          <p>{algos[current]}</p>
        </div>
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
    const summary = data.type === "qualitative" ? <QualitativeSummary data={data} /> : <UnitRange data={data} />

    return (
      <div key={uid} 
        className={SECOND_COLOUR + " grid grid-cols-1 gap-3 rounded-lg p-3"}>
        <div className="text-left grid grid-cols-5">
          <img className="col-span-2 row-span-2 h-20" 
            src={"api/" + scenario + "/images/" + data.icon} />
          <h3 className="col-span-3 font-bold">{data.name}</h3>
          <p className="col-span-3 italic">{data.description}</p>
        </div>
        <SimpleBlock colour={THIRD_COLOUR} title={"Captures"} value={capt} />
        <SimpleBlock colour={THIRD_COLOUR} title={"Limitations"} 
          value={data.limitations} />
        {summary}
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

function QualitativeSummary({data}) {

  const result = data.options.map(x => (<p>{x}</p>));
  
  return (
    <div className={"rounded-lg p-3 items-center"}>
      <p className="font-bold">Possible Values</p>
      {result}
    </div>);
}

// show the best case & worst case of metrics from the candidates
function UnitRange({data}) {

  const l = data.lowerIsBetter;
  const sigfig = sigFigs(data);

  const min_val = data.lowerIsBetter ? data.min.toFixed(sigfig) : data.max.toFixed(sigfig) * -1;
  const min_str = data.prefix + min_val + " " + data.suffix;
  const max_val = data.lowerIsBetter ? data.max.toFixed(sigfig) : data.min.toFixed(sigfig) * -1;
  const max_str = data.prefix + max_val + " " + data.suffix;

  const best_str = l ? min_str : max_str ;
  const worst_str = l ? max_str : min_str;
  const change_str = l ? "Decreases" : "Increases";

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
        onClick={() => {setPane(Pane.Pairwise)}}>
        <div className="p-4 text-5xl">
          Begin
        </div>
      </button>
  );
}

