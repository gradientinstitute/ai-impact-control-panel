import React, {useState, useEffect, useReducer, useContext} from 'react';
import { useRecoilState } from 'recoil';
import {Pane, paneState} from './Base';

export function ConstraintPane({}) {
  return (
    <div>
      <p>Constraint Pane</p>
      <StartButton />
    </div>
  );
}

function StartButton({}) {

  const [pane, setPane] = useRecoilState(paneState);
  
  return (
      <button className="bg-gray-200 text-black rounded-lg" 
        onClick={() => {setPane(Pane.Pairwise)}}>
        <div className="p-4 text-5xl">
          Ready
        </div>
      </button>
  );
}

