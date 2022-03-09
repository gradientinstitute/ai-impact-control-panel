import { useEffect, useState } from 'react';
import { atom, useRecoilState, 
  useSetRecoilState, useRecoilValue} from 'recoil';
import axios from 'axios';
import { Dialog } from "@reach/dialog";
import { Tabs, TabList, Tab, TabPanels, TabPanel, TabsOrientation } from "@reach/tabs";
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';


import {Pane, paneState, scenarioState, algoState, nameState,
        TaskTypes, taskTypeState} from './Base';

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
  const scenarios = useRecoilValue(scenariosState);
  
  if (scenarios === []) {
    return (<p>Loading...</p>);
  }

  return (
    <div className="ml-auto mr-auto w-1/2">
      <Dialog className="intro text-center" aria-label="Get Started">
        <h1 className="my-auto font-extralight mb-4 text-3xl pb-4">
          Get Started
        </h1>
        <Steps />
      </Dialog>
    </div>
  );
}

// steps of intro flow
function Steps() {
  const [tabIndex, setTabIndex] = useState(0);

 return (
   <Tabs className="intro-content flex items-stretch" index={tabIndex} onChange={setTabIndex}>
     <TabPanels className="self-center flex-1">
       <Welcome setTabIndex={setTabIndex} />
       <ChooseProblem setTabIndex={setTabIndex} />
       <ChooseScenario setTabIndex={setTabIndex}/>
     </TabPanels>
   </Tabs>
 )
}

function Welcome({setTabIndex}) {


  return (
    <TabPanel key={0}>
      <div className="text-xl grid grid-cols-1 gap-4 pb-10">
      <h2 className="text-4xl text-center">
        Welcome to the AI Impact Control panel
      </h2>

      <p>
      This tool helps decision-makers control the impacts that their AI systems
      have. It allows them to specify bounds of acceptable operation, and to
      help them achieve an acceptable balance between conlficting objectives
      (for example, performance in different customer groups).
      </p>
      
      <h2 className="text-3xl text-center">
        Live Demo
      </h2>

      <p>
      The goal of the AI Impact Control Panel is to ensure that decisions about
      how AI systems affect the world are made deliberately by the right
      decision-makers.
      </p>

      <p>
      This online demo provides a selection of simple example systems to illustrate the function of the tool. There is no ability to upload your own data or system in tis demo.
      </p>

      <p>
      To get the code or deploy the tool yourself, visit <a className="e" href="https://gradientinstitute.github.com/ai-impact-control-panel">our github</a>.
      </p>
      </div>
      <button className="btn text-2xl uppercase py-8 font-bold rounded-lg text-white"
          onClick={() => {
            setTabIndex(1);
          }}
          disabled={false}>
            Start demo
        </button>
  </TabPanel>
  )
}


function ChooseProblem({setTabIndex}) {
  // first tab: choose whether to elicit boundaries or preferences

  return (
    <TabPanel key={1}>
      <div className="grid grid-cols-1 gap-4">
        <p className="text-lg">I want to elicit</p>
        <StartButtons setTabIndex={setTabIndex} />
      </div>
  </TabPanel>
  )
}


function ChooseScenario({setTabIndex}) {
  // second tab: select scenario and eliciter (algorithm)
  const [_pane, setPane] = useRecoilState(paneState);
  const current = useRecoilValue(currentScenarioState);
  const [_scenarios, setScenarios] = useRecoilState(scenariosState);
  const [_scenario, setScenario] = useRecoilState(scenarioState);
  const [_name, setName] = useRecoilState(nameState);
  
  // const canGoBack = tabIndex >= 0;
  const taskType = useRecoilValue(taskTypeState);
  const buttonDisabled = (current === null) || (_name === "");

  // load scenarios
  useEffect(() => {
    const fetch = async () => {
      const result = await axios.get<any>("api/scenarios");
      setScenarios(result.data);
    }
    fetch();
  }, []
  );

  // Update here for additional tasks
  const nextPane = taskType == TaskTypes.Boundaries 
    ? Pane.Boundaries : Pane.Configure;


  return (
    <TabPanel key={2}>
      <div>
        <div>
          <p className="text-lg pb-6">Enter your name</p>
          <input type="text" name="name" value={_name}
            onChange={ (x) => {setName(x.target.value)}}/>
        </div>
      <br></br>
      <br></br>

      <p className="text-lg pb-6">Select a scenario</p>
      <ScenarioSelector />

      <br></br>
      <div className="flex justify-between btn-row mt-12">
        <div className="flex flex-1 align-middle text-left">
          <button className="hover:text-gray-300 transition"
            onClick={() => {
              setTabIndex(0);
            }}>
            &#8249; Back
          </button>
        </div>
        <button className="btn text-xl uppercase py-4 px-8 font-bold rounded-lg text-white"
          onClick={() => {
            if (current) {
              setScenario(current)
              setPane(nextPane);
            }
          }}
          disabled={buttonDisabled}>
          Start
        </button>
      </div>
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


// select the type of elicitation to do with two buttons
// TODO: hook up to boundary elicitation when its implemented
function StartButtons({setTabIndex}) {

  const setTask = useSetRecoilState(taskTypeState);

  return (
      <div className="grid grid-cols-2 gap-10 py-12 px-6">
        <div>
          <button className="btn mb-4 text-2xl uppercase py-8 font-bold rounded-lg text-white"
            onClick={() => {
              setTask(TaskTypes.Boundaries);            
              setTabIndex(2);
            }}
            disabled={false}>
              Boundaries
          </button>
          <p>
          Determine the boundaries of known-acceptable performance of an AI system for the purposes of model development and modelling.
          </p>
        </div>
        <div>
        <button className="mb-4 btn text-2xl uppercase py-8 font-bold rounded-lg text-white"
          onClick={() => {
            setTask(TaskTypes.Deployment);
            setTabIndex(2);
          }}
          disabled={false}>
            Deployment
        </button>
          <p>
          Determine the preferred balance of impacts for the AI system to help decide what configuration of the system should be deployed.
          </p>
        </div>
      </div>
  );
}
