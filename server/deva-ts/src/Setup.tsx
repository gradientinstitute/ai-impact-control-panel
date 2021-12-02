import { useEffect, useState } from 'react';
import { atom, useRecoilState, useRecoilValue} from 'recoil';
import axios from 'axios';
import { Dialog } from "@reach/dialog";
import { Tabs, TabList, Tab, TabPanels, TabPanel, TabsOrientation } from "@reach/tabs";
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

  // initial loading of candidates
  useEffect(() => {
    const fetch = async () => {
      const result = await axios.get<any>("scenarios");
      setScenarios(result.data);
    }
    fetch();
  }, []
  );
  
  if (_scenarios === []) {
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

// steps of intro flow
function Steps({}) {
  const [stepIndex, setStepIndex] = useState(0);

  function handleStepsChange(i) {
    setStepIndex(i);
  }

 return (
   <Tabs className="intro-content flex items-stretch" index={stepIndex} onChange={handleStepsChange}>
     <TabPanels className="self-center flex-1">
       <Step1 handleStepsChange={handleStepsChange} />
       <Step2 stepIndex={stepIndex} setStepIndex={setStepIndex}/>
     </TabPanels>
   </Tabs>
 )
}

// first step: choose what to elicit
function Step1({handleStepsChange}) {
  return (
    <TabPanel key={0}>
      <p className="text-lg">I want to elicit</p>
      <StartButtons onChange={handleStepsChange} />
  </TabPanel>
  )
}

// second step: select scenario
function Step2({stepIndex, setStepIndex}) {
  const [_pane, setPane] = useRecoilState(paneState);
  const current = useRecoilValue(currentScenarioState);
  const [_scenario, setScenario] = useRecoilState(scenarioState);

  return (
    <TabPanel key={1}>
      <p className="text-lg pb-6">Select a scenario</p>
      <ScenarioSelector />
      <div className="flex justify-between btn-row mt-12">
        <div className="flex flex-1 align-middle text-left">
          <button className="hover:text-gray-300 transition"
            onClick={() => stepIndex >=0 && setStepIndex(stepIndex-1)}>
            &#8249; Back
          </button>
        </div>
        <button className="btn text-xl uppercase py-4 px-8 font-bold rounded-lg"
          onClick={() => {
            if (current) {
              setScenario(current)
              setPane(Pane.Intro);
            }
          }}
          disabled={current === null}>
          Start
        </button>
      </div>
    </TabPanel>
  )
}

// Dropdown box for selecting a scenario
function ScenarioSelector({}) {
  
  const scenarios = useRecoilValue(scenariosState);
  const [current, setCurrent] = useRecoilState(currentScenarioState);
  const entries = Object.entries(scenarios)
  const [tabIndex, setTabIndex] = useState(-1);
  const [currentIndex, setCurrentIndex] = useState(-1)
  const tabActive = tabIndex === currentIndex && currentIndex > -1

  function handleTabsChange(i) {
    setTabIndex(i);
  }

  const tabs = entries.map(([name, v], i) => {
    return (
      <Tab
        data-current = { current === name }
        key={i}
        onMouseEnter={() => setTabIndex(i)}
        onMouseLeave={() => current ? setTabIndex(currentIndex) : setTabIndex(-1)}
        onMouseDown={() => {
          setCurrent(name);
          setCurrentIndex(i);
        }}
      >
        {v.name}
      </Tab>
    )
  })

  const tabPanels = entries.map(([name, v], i) => {
    return (
      <TabPanel key={i}>
        <span className="pr-6"><strong>Objectives:</strong> {Object.keys(v.objectives).length}</span>
        <span><strong>Metrics:</strong> {Object.keys(v.metrics).length}</span>
        <p className="pt-3">{v.operation}</p>
      </TabPanel>
    )})
  
  return (
    <Tabs
      className="scenario-selector grid grid-cols-3"
      index={tabIndex}
      orientation={TabsOrientation.Vertical}
      onChange={handleTabsChange}
    >
      <TabList className="scenario-list text-left col-span-1 font-bold">
        { tabs }
      </TabList>
      <TabPanels
        className="col-span-2 text-left py-3 px-6"
        data-active={tabActive}
      >
        { tabPanels }
      </TabPanels>
    </Tabs>
    );
}

// select the type of elicitation to do with two buttons
// TODO: hook up to boundary elicitation when its implemented
function StartButtons({onChange}) {

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

