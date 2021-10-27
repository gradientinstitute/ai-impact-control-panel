import React, {useState, useEffect, useReducer, useContext} from 'react';
import { useRecoilState } from 'recoil';
import {Pane, paneState} from './Base';

export function SetupPane({}) {


  return (
    <div>
      <p>Setup Pane</p>
      <StartButton />
      </div>
  );
}

function StartButton({}) {

  const [pane, setPane] = useRecoilState(paneState);
  
  return (
      <button className="bg-gray-200 text-black rounded-lg" 
        onClick={() => {setPane(Pane.Intro)}}>
        <div className="p-4 text-5xl">
          Ready
        </div>
      </button>
  );
}

