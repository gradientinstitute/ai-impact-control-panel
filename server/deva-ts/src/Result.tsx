import { useEffect } from 'react';
import { useRecoilValue, useRecoilState } from 'recoil';
import axios from 'axios';

import {Key, Model, adjustUnitRange} from './Widgets';
import {metadataState, Pane, resultState} from './Base';
import {HelpOverlay, overlayRank, helpState, getOverlayBoundary} from './HelpOverlay';

// main pane
export function ResultPane({}) {

  const metadata = useRecoilValue(metadataState);
  const [result, setResult] = useRecoilState(resultState);
  const [help, setHelpState] = useRecoilState(helpState);

  useEffect(() => {
    const fetch = async () => {
      const res = await axios.get<any>("api/deployment/result");
      const d = res.data;
      setResult(d);
    }
    fetch();
    setHelpState(getOverlayBoundary(Pane.Result).start);
  }, []
  );

  if (result === null) {
    return (
      <div>Loading...</div>
    );
  }

  const [name, attr_spec] = Object.entries(result)[0];
  const attr = attr_spec["attr"]
  const spec = attr_spec["spec"]


  function comparisons() {
    let result = []; 
    for (let [uid, u] of Object.entries(metadata.metrics)) {

      let value = attr[uid];
      if (!u['lowerIsBetter']) {
        u = adjustUnitRange(u);
        value *= -1;
      }
    
      result.push(
      <div className="bg-gray-700 rounded-lg p-3">
        <ResultOnMetric
          key={uid}
          unit={u} 
          value={value} 
        />
      </div>
      );
    }
    return result;
  }

  return (
    <div className="mx-auto max-w-screen-lg pb-8 grid gap-x-8 gap-y-6
      grid-cols-1 text-center items-center">
      <h2 className="text-2xl mb-4"> Preference elicitation concluded.
        <br /> Your most preferred system is

        <div className="inline italic"> {name}</div>.
      </h2>
      <HelpOverlay 
        rank={overlayRank.Results}
        title={"Results"} 
        msg={"Here are the results"} 
        placement={"top"}
      >
      <h1 className="text-4xl">{name} Impacts</h1>
      </HelpOverlay>

      {comparisons()}
      <p>
        See <b>metrics_{spec}.toml</b> and <b>params_{spec}.toml</b> for more
        details of {name}.
      </p>
      <HelpOverlay 
        rank={overlayRank.DownloadSessionLog}
        title={"Download Session Log"} 
        msg={"Click here to download a record of your session"} 
        placement={"bottom"}
      >
      <p>
        Click to download
        the <a href={"api/deployment/logs/txt"} download><b>session log</b></a>.
      </p>
      </HelpOverlay>
      <StartOver />
    </div>
  );
}

function StartOver({}) {
  return (
      <button className="bg-gray-200 text-black rounded-lg mb-3" 
        onClick={() =>  window.location.href='/'}>
        <div className="p-4 text-5xl">
          Start Over
        </div>
      </button>
  );
}


function ResultOnMetric({value, unit}) {

  return (
    <div className="grid grid-cols-12">
      <div className="my-auto col-span-3">
        <Key unit={unit}/>
      </div>
      <div className="col-span-9">
        <Model unit={unit} name={"The chosen system"} 
          value={value} isMirror={false}/>
      </div>
    </div>

  );
}

