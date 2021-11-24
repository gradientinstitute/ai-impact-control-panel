import { useEffect } from 'react';
import { atom, useRecoilState, useRecoilValue} from 'recoil';
import axios from 'axios';
import { Dialog, DialogOverlay, DialogContent } from "@reach/dialog";
import "@reach/dialog/styles.css";

import {Pane, paneState, scenarioState} from './Base';


// the set of scenarios retrieved from the serever
const scenariosState = atom({
  key: 'scenarios',
  default: [],
});

// the currently selected scenario from the selection dropdown
const currentScenarioState = atom({
  key: 'currentScenario',
  default: null,
});

// the setup pane itself (ie root component)
export function SetupPane({}) {

  const [_scenarios, setScenarios] = useRecoilState(scenariosState);
  const [current, setCurrent] = useRecoilState(currentScenarioState);

  // initial loading of candidates
  useEffect(() => {
    const fetch = async () => {
      const result = await axios.get<any>("scenarios");
      setScenarios(result.data);
      setCurrent(Object.keys(result.data)[0]);
    }
    fetch();
  }, []
  );
  
  if (current === null) {
    return (<p>Loading...</p>);
  }

  return (
    <div>
      <div className="ml-auto mr-auto w-1/2">
        <Dialog>        
          <h1 className="my-auto text-center mb-4">Get Started</h1>
          <StartButtons />
        </Dialog>
        <h1 className="my-auto text-center mb-4">Select a scenario</h1>
          <Summary />
      </div>
    </div>
  );
}

// Dropdown box for selecting a scenario
function ScenarioSelector({}) {
  
  const scenarios = useRecoilValue(scenariosState);
  const [current, setCurrent] = useRecoilState(currentScenarioState);
  
  const elements = Object.entries(scenarios).map(([name, v]) => {
    return (<option key={name} value={name}>{v.name}</option>);
  });
  
  return (
      <div className="p-4 gap-4 bg-gray-500 grid grid-cols-3" >
        <p className="text-right col-span-1">Scenario</p>
        <select className="col-span-2" name="scenarios" value={current} 
          onChange={ (x) => {setCurrent(x.target.value)}}>
          {elements}
        </select>
      </div>
    );
}

// Summary of the currently selected scenario
function Summary({}) {
  
  const scenarios = useRecoilValue(scenariosState);
  const current = useRecoilValue(currentScenarioState);

  const desc_string = "A system " + scenarios[current].purpose;
  const n_obj = Object.keys(scenarios[current].objectives).length;
  const n_met = Object.keys(scenarios[current].metrics).length;

  return (
    <div className="grid grid-cols-2 rounded-lg bg-gray-600 gap-4 p-4">
      <div className="col-span-2">
        <ScenarioSelector />
      </div>
      <div className="col-span-2 rounded-lg bg-orange-700 py-4">
        <h2 className="text-center">{scenarios[current].name}</h2>
        <p className="text-center italic px-4">{desc_string}</p>
      </div>
      <p className="text-center py-2 rounded-lg bg-green-700">
        {"Objectives: " + n_obj}
      </p>
      <p className="text-center py-2 rounded-lg bg-green-700">
        {"Metrics: " + n_met}
      </p>
      <p className="col-span-2">{scenarios[current].operation}</p>
    </div>
  );
}

// select the type of elicitation to do with two buttons
// TODO: hook up to boundary elicitation when its implemented
function StartButtons({}) {
  
  const [_pane, setPane] = useRecoilState(paneState);
  const current = useRecoilValue(currentScenarioState);
  const [_scenario, setScenario] = useRecoilState(scenarioState);

  return (
      <div className="grid grid-cols-2 gap-10 py-10">
        <button className="bg-gray-200 text-black rounded-lg" 
          onClick={() => {
            setScenario(current);
            setPane(Pane.Intro); 
          }}
          disabled={true}>
          <div className="p-4 text-lg">
            Elicit Boundaries
          </div>
        </button>
        <button className="bg-gray-200 text-black rounded-lg" 
          onClick={() => {
            setScenario(current);
            setPane(Pane.Intro); 
          }}
          disabled={false}>
          <div className="p-4 text-lg">
            Elicit Deployment
          </div>
        </button>
      </div>
  );
}

