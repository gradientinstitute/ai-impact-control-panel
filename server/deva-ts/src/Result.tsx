// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
import { useEffect } from 'react';
import { useRecoilValue, useRecoilState } from 'recoil';
import axios from 'axios';

import {Key, Model, adjustUnitRange} from './Widgets';
import {metadataState, resultState} from './Base';
// import {HelpOverlay, overlayId, helpState} from './HelpOverlay';

// main pane
export function ResultPane() {

  const metadata = useRecoilValue(metadataState);
  const [result, setResult] = useRecoilState(resultState);
  // const [help, setHelpState] = useRecoilState(helpState);

  useEffect(() => {
    const fetch = async () => {
      const res = await axios.get<any>("api/deployment/result");
      const d = res.data;
      setResult(d);
    }
    fetch();
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
      <p className="text-3xl pb-4">
        Click to download
        the <a href={"api/deployment/logs/txt"} download><b>session log</b></a>.
      </p>
        <h1 className="text-4xl">{name} Impacts</h1>

      {comparisons()}
      <p className="py-4">
        See <b>metrics_{spec}.toml</b> and <b>params_{spec}.toml</b> in your scenario folder for more details of {name}.
      </p>
      <StartOver />
    </div>
  );
}

function StartOver() {
  return (
      <div className="grid grid-cols-3">
      <div className="col-span-1" />
      <button className="btn text-2xl uppercase py-8 font-bold rounded-lg text-white"
        onClick={() =>  window.location.reload()}>
        <div className="p-4 text-5xl">
          Start Over
        </div>
      </button>
      <div className="col-span-1" />
      </div>
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

