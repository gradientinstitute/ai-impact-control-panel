import { useEffect, useState } from 'react';
import { atom, useRecoilState, useRecoilValue} from 'recoil';
import axios from 'axios';
import { Dialog, DialogOverlay, DialogContent } from "@reach/dialog";
import { Tabs, TabList, Tab, TabPanels, TabPanel } from "@reach/tabs";
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';

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
      const result = await axios.get<any>("api/scenarios");
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
    <div className="ml-auto mr-auto w-1/2">
      <Dialog className="intro text-center">
        <h1 className="my-auto font-extralight mb-4 text-3xl pb-4">Get Started</h1>
        <Steps />
      </Dialog>
    </div>
  );
}

// each step of intro flow
function Steps({}) {
  const [stepIndex, setStepIndex] = useState(0);
  const [_pane, setPane] = useRecoilState(paneState);
  const current = useRecoilValue(currentScenarioState);
  const [_scenario, setScenario] = useRecoilState(scenarioState);

  function handleStepsChange(i) {
    setStepIndex(i);
  }

 return (
   <Tabs className="intro-content flex items-stretch" index={stepIndex} onChange={handleStepsChange}>
     <TabPanels className="self-center flex-1">
       <TabPanel key={0}>
          <p className="text-lg">I want to elicit</p>
          <StartButtons onChange={handleStepsChange} />
       </TabPanel>
       <TabPanel key={1}>
        <Summary />
        <div className="flex justify-between btn-row my-4">
        <div className="flex flex-1 align-middle text-left">
          <button className="hover:text-gray-300 transition"
            onClick={() => stepIndex >=0 && setStepIndex(stepIndex-1)}>
            &#8249; Back
          </button>
        </div>
        <button className="btn text-xl uppercase py-4 px-8 font-bold rounded-lg"
          onClick={() => {
            setScenario(current);
            setPane(Pane.Intro);
          }}
          disabled={false}>
          Start
        </button>
        </div>
       </TabPanel>
     </TabPanels>
   </Tabs>
 )
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
function StartButtons({onChange}) {
  
  const current = useRecoilValue(currentScenarioState);

  return (
      <div className="grid grid-cols-2 gap-10 py-12 px-6">
        <button className="btn text-2xl uppercase py-8 font-bold rounded-lg"
          onClick={() => {
            onChange(1);
          }}
          disabled={true}>
            Boundaries
        </button>
        <button className="btn text-2xl uppercase py-8 font-bold rounded-lg"
          onClick={() => {
            onChange(1);
          }}
          disabled={false}>
            Deployment
        </button>
      </div>
  );
}

