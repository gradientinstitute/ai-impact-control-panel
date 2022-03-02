import { useRecoilValue } from 'recoil';
import _ from "lodash";

import { metadataState } from './Base';
import {HelpOverlay, overlayId, HelpButton, helpState} from './HelpOverlay';

// the Introduction pane -- root node
export function IntroContext({}) {
  
  const metadata = useRecoilValue(metadataState);

  if (metadata === null) {
    return (<p>Loading...</p>);
  }

  return (
    <div className="grid gap-4 grid-cols-1">

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
  <HelpOverlay hid={overlayId.Scenario}>
    <div className="bg-gray-700 gap-4 p-4 grid grid-cols-1">

      <h1 className="text-left">Scenario Details</h1>
      <h2 className=""> {metadata.name} </h2>
      <p className="italic">
        {metadata.purpose}
      </p>
      <p>
        <span className="font-bold">Operation:</span> {metadata.operation}
      </p>
    </div>
  </HelpOverlay>
  );


}

// visual-ish display of the data -> model -> decision pipeline
function Pipeline({}) {

  const metadata = useRecoilValue(metadataState);

  return (
    <div className= "p-4 grid grid-cols-1 bg-gray-700 text-center">
      <h2 className="mb-3 font-bold font-xl">Pipeline</h2>

      <div className="bg-gray-600 p-4">
        <h2 className="font-bold">Data</h2>
        <p>{metadata.data}</p>
      </div>
      <div className="p-4 bg-gray-500">
        <BlockWithSubBlocks 
          items={metadata.targets} 
          title={"Predictions"}
          css={""}
          />
      </div>

      <div className="bg-gray-600 p-4">
        <h2 className="font-bold">Decision Rules</h2>
        <p>{metadata.decision_rules}</p>
      </div>

      <div className="bg-gray-500 p-4">
        <BlockWithSubBlocks
          items={metadata.actions}
          title={"Actions"}
          css={"bg-grey-800"}
          />
      </div>

    </div>
  );
}

function ObjectiveBlock({title, items}) {
  const mapped_items = Object.entries(items).map(([name, v]) => {
    return (
      <div key={name} className="mb-4">
        <h3 className="font-bold">{v["name"]}</h3>
        <p>{v["description"]}</p>
      </div>
    );
  });
  return (
    <div className="p-3 bg-gray-700">
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

