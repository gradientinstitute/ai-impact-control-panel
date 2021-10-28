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

const passwordState = atom({
  key: 'password',
  default: "",
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
      <h1 className="my-auto text-center mb-4">Login</h1>
      <div className="grid grid-cols-4 gap-4 p-4">
        <div className="col-span-2">
          <Login />
        </div>
        <div className="col-span-2">
          <Summary />
        </div>
      </div>
      </div>
  );
}

function Login({}) {
  
  const scenarios = useRecoilValue(scenariosState);
  const [current, setCurrent] = useRecoilState(currentScenarioState);
  const [_login, setLogin] = useRecoilState(loginState);
  const [_pword, setPword] = useRecoilState(passwordState);

  const elements = Object.entries(scenarios).map(([name, v]) => {
    return (<option value={name}>{v.name}</option>);
  });
  
  return (
      <div className="p-4 gap-4 rounded-lg bg-blue-700 grid grid-cols-3" >
        <p className="text-right col-span-1">Scenario</p>
        <select className="col-span-2" name="scenarios" value={current} 
          onChange={
            (x) => {setCurrent(x.target.value)}}>
          {elements}
        </select>
        <p className="text-right col-span-1">login</p>
        <input className="col-span-2" type="text" name="username" 
          onChange={
            (x) => {setLogin(x.target.value)}}/>
        <p className="text-right col-span-1">password</p>
        <input className="col-span-2" type="password" name="username" 
          onChange={
            (x) => {setPword(x.target.value)}}/>
        <div className="col-span-3">
          <StartButtons />
        </div>
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
      <div className="grid grid-cols-2 rounded-lg bg-gray-600 gap-4 p-4">
        <div className="col-span-2 rounded-lg bg-orange-700 py-4">
          <h2 className="text-center">{scenarios[current].name}</h2>
          <p className="text-center italic px-4">{"A system " + scenarios[current].purpose}</p>
        </div>
        <p className="col-span-2">{scenarios[current].operation}</p>
        <p className="text-center py-2 rounded-lg bg-green-700">{"Objectives: " + Object.keys(scenarios[current].objectives).length}</p>
        <p className="text-center py-2 rounded-lg bg-green-700">{"Metrics: " + Object.keys(scenarios[current].metrics).length}</p>
      </div>);
}

function StartButtons({}) {

  const [_pane, setPane] = useRecoilState(paneState);
  const current = useRecoilValue(currentScenarioState);
  const login = useRecoilValue(loginState);
  const pword = useRecoilValue(passwordState);

  const disabled = (current === null 
    || login.length === 0 
    || pword.length === 0);
  
  return (
      <div className="grid grid-cols-2 gap-4 p-4">
        <button className="bg-gray-200 text-black rounded-lg" 
          onClick={() => {setPane(Pane.Intro)}}
          disabled={true}>
          <div className="p-4 text-lg">
            Elicit Boundaries
          </div>
        </button>
        <button className="bg-gray-200 text-black rounded-lg" 
          onClick={() => {setPane(Pane.Intro)}}
          disabled={disabled}>
          <div className="p-4 text-lg">
            Elicit Deployment
          </div>
        </button>
      </div>
  );
}

