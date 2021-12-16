import { useEffect, useState } from 'react';
import { atom, useRecoilState, useRecoilValue} from 'recoil';
import axios from 'axios';
import { Dialog } from "@reach/dialog";
import { Tabs, TabList, Tab, TabPanels, TabPanel, TabsOrientation } from "@reach/tabs";
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';

import {Pane, paneState, scenarioState, algoState} from './Base';


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

// the set of algorithms retrieved from the serever
const algoChoicesState = atom({
    key: 'algorithmChoices',
    default: [],
  });

// the setup pane itself (ie root component)
export function SetupPane({}) {

  const [_scenarios, setScenarios] = useRecoilState(scenariosState);
  // algorithms / eliciters
  const [algorithms, setAlgos] = useRecoilState(algoChoicesState);
  const [_current, setCurrent] = useRecoilState(algoState);
  
  // initial loading of candidates
  useEffect(() => {
    const fetch = async () => {
      const result = await axios.get<any>("api/scenarios");
      setScenarios(result.data);
    }
    fetch();
  }, []
  );

  // use effect for algo. asyn
  useEffect(() => {
    const fetch = async () => {
      const elic = await axios.get<any>("api/algorithms");
      setAlgos(elic.data);
    }
    fetch();
  }, []
  );
      
  useEffect( () => {
    if (algorithms !== null) {
      setCurrent(Object.keys(algorithms)[0]);
    }
  }, [algorithms]);

  if (_scenarios === []) {
    return (<p>Loading...</p>);
  }

  return (
    <div className="ml-auto mr-auto w-1/2">
      <Dialog className="intro text-center" aria-label="Get Started">
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

// second step: select scenario and eliciter (algorithm)
function Step2({stepIndex, setStepIndex}) {
  const [_pane, setPane] = useRecoilState(paneState);
  const current = useRecoilValue(currentScenarioState);
  const [_scenario, setScenario] = useRecoilState(scenarioState);
  const canGoBack = stepIndex >= 0;
  const buttonDisabled = current === null;

  return (
    <TabPanel key={1}>
      <p className="text-lg pb-6">Select a scenario</p>
      <ScenarioSelector />
      <br></br>
      <p className="text-lg pb-6">Select an algorithm</p>
      <AlgoSelector />
      <div className="flex justify-between btn-row mt-12">
        <div className="flex flex-1 align-middle text-left">
          <button className="hover:text-gray-300 transition"
            onClick={() => canGoBack && setStepIndex(stepIndex-1)}>
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
          disabled={buttonDisabled}>
          Start
        </button>
      </div>
    </TabPanel>
  )
}

// Select scenario from list and preview details
function ScenarioSelector({}) {
  
  const scenarios = useRecoilValue(scenariosState);
  const [current, setCurrent] = useRecoilState(currentScenarioState);
  const entries = Object.entries(scenarios);
  const [tabIndex, setTabIndex] = useState(-1);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const tabActive = tabIndex === currentIndex && currentIndex > -1;

  function handleTabsChange(i) {
    setTabIndex(i);
  }

  const tabs = entries.map(([name, v], i) => {
    const indexOnLeave = current ? currentIndex : -1;
    const isSelectedTab = current === name;

    return (
      <Tab
        data-current = { isSelectedTab }
        key={i}
        onMouseEnter={() => setTabIndex(i)}
        onMouseLeave={() => setTabIndex(indexOnLeave)}
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
    const numObjectives = Object.keys(v.objectives).length;
    const numMetrics = Object.keys(v.metrics).length;

    return (
      <TabPanel key={i}>
        <span className="pr-6"><strong>Objectives:</strong> {numObjectives}</span>
        <span><strong>Metrics:</strong> {numMetrics}</span>
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
        {tabs}
      </TabList>
      <TabPanels
        className="col-span-2 text-left py-3 px-6"
        data-active={tabActive}
      >
        {tabPanels}
      </TabPanels>
    </Tabs>
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

