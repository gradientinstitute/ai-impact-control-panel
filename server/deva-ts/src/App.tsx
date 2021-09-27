import React, {useState, useEffect} from 'react';
import axios from 'axios';
import {MainPane} from './Pairwise';
import {IntroPane} from './Intro';
import {ResultPane} from './Result';
import './App.css';

function App() {

  // they've read and understood the problem setup
  const [ready, setReady] = useState(false);
  // the metadata for the problem
  const [units, setUnits] = useState<any>(null);
  // the result that comes back at the end
  const [result, setResult] = useState(null);

  // initial request on load
  useEffect(() => {
    let req = "metadata";
    async function fetchData() {
      const result = await axios.get<any>(req);
      setUnits(result.data);
    }
    fetchData();
  }, []
  );
  
  let pane = (<h2>Loading...</h2>);
  if (units != null && ready === false) {
    pane = (<IntroPane units={units} onClick={() => {setReady(true)}}/>);
  } else if (units!= null && ready === true && result == null) {
    pane = (<MainPane units={units} setResult={setResult} />)
  } else if (units != null && ready === true && result != null) {
    pane = (<ResultPane units={units} result={result}/>);
  } 

  return (
    <div className="App mx-auto pt-8 bg-gray-300">
      <h1 className="pb-8">AI Governance Control Panel</h1>
      {pane}
    </div>
  );
}



export default App;
