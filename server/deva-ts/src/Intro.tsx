import React, {useState, useEffect, useReducer, useContext} from 'react';

export function IntroPane(props) {

  function rows() {
    let result = [];
    for (const [name, d] of Object.entries(props.units)) {
      const deets = JSON.stringify(d, null, 2);
      result.push(
        <div key={name}>
          <h2>{name}</h2>
          <pre className="text-left">{deets}</pre>
        </div>
      );
    }
    return result;
  }

  return (
    <div>
      <h1> Intro material </h1>
      <div className="flex flex-wrap space-x-10 mt-8">
        {rows()}
      </div>
      <ReadyButton onClick={props.onClick} />
    </div>
  );
}

function ReadyButton(props) {
  return (
      <button className="bg-yellow-300 rounded-lg" 
        onClick={() => props.onClick()}>
        <div className="p-4">
          Begin
        </div>
      </button>
  );
}

