import React, {useState, useEffect, useReducer, useContext} from 'react';

export function ResultPane(props) {
  const deets = JSON.stringify(props.result, null, 2)
  return (
    <div>
      <h1> Result model </h1>
      <pre>{deets} </pre>
    </div>
  );
}

