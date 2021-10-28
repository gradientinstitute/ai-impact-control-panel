import React, {useState, useEffect, useReducer, useContext} from 'react';
import { atom, useRecoilState, useRecoilValue} from 'recoil';
import {Pane, paneState, loginState, scenarioState} from './Base';
import axios from 'axios';

const scenariosState = atom({
  key: 'scenarios',
  default: [],
});

const currentScenarioState = atom({
  key: 'currentScenario',
  default: null,
});

export function SetupPane({}) {

  const [_scenarios, setScenarios] = useRecoilState(scenariosState);
  const [_current, setCurrent] = useRecoilState(currentScenarioState);
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


  return (
    <div>
      <h1 className="my-auto text-center">Setup Pane</h1>
      <div className="grid grid-cols-4 gap-4 p-4">
        <div className="col-span-1">
          <Login />
        </div>
        <div className="col-span-3">
          <Summary />
        </div>
      </div>
      <StartButton />
      </div>
  );
}

function Login({}) {
  
  const scenarios = useRecoilValue(scenariosState);
  const [current, setCurrent] = useRecoilState(currentScenarioState);
  const [_login, setLogin] = useRecoilState(loginState);

  const elements = Object.entries(scenarios).map(([name, v]) => {
    return (<option value={name}>{v.name}</option>);
  });
  
  return (
      <div className="p-4 gap-4 grid grid-cols-3" >
        <p className="text-right col-span-1">login</p>
        <input className="col-span-2" type="text" name="username" 
          onChange={
            (x) => {setLogin(x.target.value)}}/>
        <p className="text-right col-span-1">password</p>
        <input className="col-span-2" type="password" name="username" />

        <p className="text-right col-span-1">Scenario</p>
        <select className="col-span-2" name="scenarios" value={current} 
          onChange={
            (x) => {setCurrent(x.target.value)}}>
          {elements}
        </select>
      </div>
    );
}

function Summary({}) {
  
  const scenarios = useRecoilValue(scenariosState);
  const current = useRecoilValue(currentScenarioState);
  
  if (current === null) {
    return (<p>Loading...</p>);
  }
  return (
      <div>
        <h1>{scenarios[current].name}</h1>
        <p>{"Purpose: " + scenarios[current].purpose}</p>
        <p>{"Operation: " + scenarios[current].operation}</p>
        <p>{"Objectives: " + Object.keys(scenarios[current].objectives).length}</p>
        <p>{"Metrics: " + Object.keys(scenarios[current].metrics).length}</p>
      </div>);
}

function StartButton({}) {

  const [_pane, setPane] = useRecoilState(paneState);
  const current = useRecoilValue(currentScenarioState);
  const login = useRecoilValue(loginState);
  
  return (
      <button className="bg-gray-200 text-black rounded-lg" 
        onClick={() => {setPane(Pane.Intro)}}
        disabled={current===null || login===null}>
        <div className="p-4 text-5xl">
          Ready
        </div>
      </button>
  );
}

