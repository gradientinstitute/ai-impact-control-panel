import { useState, useEffect } from 'react';
import { atom, useRecoilState, useRecoilValue } from 'recoil';
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

  // algorithms / eliciters
  // const algo = useRecoilValue(algoState);
  
  // all candidates sent to us by the server
  const [_current, setCurrent] = useRecoilState(algoState);
  const [metadata, setMetadata] = useRecoilState(metadataState);
  const [algorithms, setAlgos] = useRecoilState(algoChoicesState);
  const [allCandidates, setAllCandidates] = useRecoilState(allCandidatesState);
  const maxRanges = useRecoilValue(maxRangesState);
  const [_constraints, setConstraints] = useRecoilState(constraintsState);

  const [_pane, setPane] = useRecoilState(paneState);

  // initial request on load
  useEffect(() => {
    let req = "api/scenarios/" + scenario;
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

  if (_allCandidates === null) {
    return (<p>Loading...</p>);
  }

  const bounds = metadata.bounds;
  const candidates = filterCandidates(_allCandidates, bounds);

    if(candidates.length == 0){
        setPane(Pane.UserReport);
    }

  return (
    <div className="grid grid-cols-7 gap-8 pb-10">
      <div className="col-span-2">
        <IntroContext />
      </div>
      <div className="col-span-5">
        <EliminatedStatus remaining={candidates} all={_allCandidates}/>
        <Constraints />
        <AlgorithmMenu />
        <StartButton />
      </div>
    </div>
  );
}


function EliminatedStatus({remaining, all}) {

  const eliminated = all.length - remaining.length;

  return (
  <div className="mb-8 bg-gray-600 rounded-lg">
    <span className="italic text-2xl">
      {eliminated +" of " + all.length + " "}
    </span>
    candidates are eliminated by the system requirement bounds
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

  // some local state to trigger a useEffect fetcher
  const [submit, setSubmit] = useState(false);

  const name = useRecoilValue(nameState);
  const scenario = useRecoilValue(scenarioState);
  const constraints = useRecoilValue(constraintsState);
  const [_pane, setPane] = useRecoilState(paneState);
  const algorithm = useRecoilValue(algoState);

  const payload = {
    scenario: scenario,
    constraints: constraints,
    name: name,
    algorithm: algorithm,
  };

  useEffect(() => {
    const fetch = async () => {
      await axios.put<any>("api/deployment/new", payload);
      setPane(Pane.Pairwise);
    }
    if (submit) {
      fetch();
    }
  }, [submit]
  );

  return (
      <div className="">
      <button className="bg-gray-200 text-black" 
        onClick={() => {setSubmit(true)}}>
        <div className="p-4 text-3xl">
          Continue
        </div>
      </button>
      </div>
  );
}
