import { useEffect } from 'react';
import { atom, useRecoilState, useRecoilValue } from 'recoil';
import { ArcherContainer, ArcherElement } from 'react-archer';
import _ from "lodash";
import axios from 'axios';

import { Pane, paneState, algoState, nameState, constraintsState,
         metadataState, scenarioState} from './Base';
import {sigFigs} from './Widgets';
import {IntroContext} from './Intro';
import {Constraints} from './Constrain';

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

  if (metadata === null) {
    return (<p>Loading...</p>);
  }

  return (
    <div className="grid grid-cols-7">
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
        <p className="text-right col-span-1">Eliciter</p>
        <select className="col-span-8" name="scenarios" value={current} 
          onChange={ (x) => {setCurrent(x.target.value)}}>
          {elements}
        </select>
        <div className="col-span-10">
          <p>{algos[current]}</p>
        </div>
      </div>
    );

}

function StartButton({}) {

  const setSubmit = (x) => {};
  // const [submit, setSubmit] = useState(false);

  // const scenario = useRecoilValue(scenarioState);
  // const constraints = useRecoilValue(constraintsState);
  // const [_pane, setPane] = useRecoilState(paneState);

  // useEffect(() => {
  //   const fetch = async () => {
  //     await axios.put<any>("api/" + scenario + "/constraints", constraints);
  //     setPane(Pane.Pairwise);
  //   }
  //   if (submit) {
  //     fetch();
  //   }
  // }, [submit]
  // );

  return (
      <button className="bg-gray-200 text-black rounded-lg" 
        onClick={() => {setSubmit(true)}}>
        <div className="p-4 text-3xl">
          Continue
        </div>
      </button>
  );
}
