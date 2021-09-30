import React, {useState, useEffect, useReducer, useContext} from 'react';
import {Key, Model} from './Widgets';

export function ResultPane(props) {
  const metadata = props.metadata;
  const [name, value] = Object.entries(props.result)[0];

  function comparisons() {
    let result = []; 
    for (const [uid, u] of Object.entries(metadata.metrics)) {
      result.push(
      <div className="bg-gray-700 rounded-lg p-3">
        <ResultOnMetric
          key={uid}
          unit={u} 
          value={value[uid]} 
          name={uid} 
        />
      </div>
      );
    }
    return result;
  }

  return (
    <div className="mx-auto max-w-screen-lg pb-8 grid gap-x-8 gap-y-6
      grid-cols-1 text-center items-center">
      <h2 className="text-2xl mb-4"> Preference elicitation concluded.
        <br /> Your most preferred system is
        <div className="inline italic"> {name}</div>.
      </h2>
      <h1 className="text-4xl">{name} Impacts</h1>
      {comparisons()}
      <StartOver />
    </div>
  );
}

function StartOver(props) {
  return (
      <button className="bg-gray-200 text-black rounded-lg mb-3" 
        onClick={() =>  window.location.href='/'}>
        <div className="p-4 text-5xl">
          Start Over
        </div>
      </button>
  );
}


function ResultOnMetric(props) {

  return (
    <div className="grid grid-cols-12">
      <div className="my-auto col-span-3">
        <Key unit={props.unit}/>
      </div>
      <div className="col-span-9">
        <Model unit={props.unit} name={props.name} 
          value={props.value} mirror={false}/>
      </div>
    </div>

  );
}

