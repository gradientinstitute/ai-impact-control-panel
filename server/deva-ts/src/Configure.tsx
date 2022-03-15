// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
import { useState, useEffect } from 'react';
import { atom, useRecoilState, useRecoilValue, useSetRecoilState} from 'recoil';
import { ArcherContainer, ArcherElement } from 'react-archer';
import _ from "lodash";
import axios from 'axios';

import { Pane, paneState, algoState, nameState, constraintsState,
         metadataState, scenarioState, algoChoicesState} from './Base';
import {sigFigs} from './Widgets';
import {IntroContext} from './Intro';
import {Constraints} from './Constrain';
import { maxRangesState } from './ConstrainScrollbar';

import { filterCandidates } from './ConstrainScrollbar';
import {HelpOverlay, overlayId, HelpButton, helpState} from './HelpOverlay';


// TODO siigh css? 
const HIGHLIGHT_COLOUR = "bg-orange-700";
const FIRST_COLOUR = "bg-gray-700";
const SECOND_COLOUR = "bg-blue-600";
const THIRD_COLOUR = "bg-green-700";

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

  // all candidates sent to us by the server
  const [_current, setCurrent] = useRecoilState(algoState);
  const [metadata, setMetadata] = useRecoilState(metadataState);
  const [algorithms, setAlgos] = useRecoilState(algoChoicesState);
  const [allCandidates, setAllCandidates] = useRecoilState(allCandidatesState);
  const maxRanges = useRecoilValue(maxRangesState);
  const [_constraints, setConstraints] = useRecoilState(constraintsState);
  const [_pane, setPane] = useRecoilState(paneState);
  const setHelpState = useSetRecoilState(helpState);

  // initial request on load
  useEffect(() => {
    let req = "api/scenarios/" + scenario;
    async function fetchData() {
      const result = await axios.get<any>(req);
      const d = result.data;
      setMetadata(d.metadata);
      setAlgos(d.algorithms);
      setAllCandidates(d.candidates);
      setHelpState(overlayId.ToggleHelp);
    }
    fetchData();
  }, []
  );

  useEffect(() => {
    setConstraints(maxRanges);
  }, [allCandidates]);
  

  // default selection of a particular algorithm
  useEffect( () => {
    if (algorithms !== null) {
      setCurrent(Object.keys(algorithms)[0]);
    }
  }, [algorithms]);

  if (metadata === null) {
    return (<p>Loading...</p>);
  }

  if (allCandidates === null) {
    return (<p>Loading...</p>);
  }

  let candidates = allCandidates  
  if ("bounds" in metadata){
    const bounds = metadata.bounds;
    candidates = filterCandidates(allCandidates, bounds);
  }

  if(candidates.length == 0){
      setPane(Pane.UserReport);
  }

  return (
    <div className="grid grid-cols-7 gap-8 pb-10">
      <div className="col-span-2">
        <IntroContext />
      </div>
      <div className="col-span-5">
        <Constraints />
        <AlgorithmMenu />
        <StartButton />
      </div>
    </div>
  );
}



function AlgorithmMenu({}) {
  
  return (
    <div>
      <h1 className="text-left">Elicitation Settings</h1>
      <AlgoSelector />
    </div>
  );

}

// Select algorithm from list and preview details
function AlgoSelector({}) {
  
  const algos = useRecoilValue(algoChoicesState);
  const [current, setCurrent] = useRecoilState(algoState);

  const elements = Object.entries(algos).map(([name, d]) => {
    return (<option key={name} value={name}>{name}</option>);
  });
  
  return (
      <div className="p-4 gap-4 grid grid-cols-10" >
        <div className="col-span-1">
          <p className="text-right">Eliciter</p>
        </div>
        <div className="col-span-9">
          <select className="" name="scenarios" value={current} 
            onChange={ (x) => {setCurrent(x.target.value)}}>
            {elements}
          </select>
        </div>
        <div className="col-span-1">
        </div>
        <div className="col-span-9">
          <p>{algos[current]}</p>
        </div>
      </div>
    );

}


function StartButton({}) {

  const [_pane, setPane] = useRecoilState(paneState);

  return (
      <div className="">
      <button className="bg-gray-200 text-black" 
        onClick={() => {setPane(Pane.Pairwise)}}>
        <div className="p-4 text-3xl">
          Continue
        </div>
      </button>
      </div>
  );
}
