import React, {useState, useEffect} from 'react';
import axios from 'axios';
import {MainPane} from './Pairwise';
import {IntroPane} from './Intro';
import {ResultPane} from './Result';
import './App.css';
import logo from './logo-dark-small.svg';

function App() {

  // they've read and understood the problem setup
  const [ready, setReady] = useState(false);
  // the metadata for the problem
  const [metadata, setMetadata] = useState<any>(null);
  // the result that comes back at the end
  const [result, setResult] = useState(null);

  // initial request on load
  useEffect(() => {
    let req = "metadata";
    async function fetchData() {
      const result = await axios.get<any>(req);
      setMetadata(result.data);
    }
    fetchData();
  }, []
  );
  
  let pane = (<h2>Loading...</h2>);
  if (metadata != null && ready === false) {
    pane = (<IntroPane metadata={metadata} onClick={() => {setReady(true)}}/>);
  } else if (metadata!= null && ready === true && result == null) {
    pane = (<MainPane metadata={metadata} setResult={setResult} />)
  } else if (metadata != null && ready === true && result != null) {
    pane = (<ResultPane metadata={metadata} result={result}/>);
  } 

  return (
    <div className="App container text-gray-200 mx-auto mb-32 px-8 pt-8 bg-gray-800">
      <div className="grid grid-cols-12 text-center items-center mb-8">
        <img className="col-span-2 h-16" src={logo} alt="Gradient Institute logo" />
        <h1 className="col-span-8 text-3xl">AI Impact Governance Software</h1>
        <div className="col-span-2" />
      </div>
      {pane}
    </div>
  );
}


export default App;
