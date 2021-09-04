import React, {useState, useEffect} from 'react';
import axios from 'axios';
import './App.css';

function App() {
  return (
    <div className="App container mx-auto text-center">
          <h1>AI Governance Control Panel</h1>
          <PairwiseComparator />
    </div>
  );
}

type ModelChoice = {
  model1: string,
  model2: string
}

// https://codesandbox.io/s/jvvkoo8pq3?file=/src/index.js
// https://www.robinwieruch.de/react-hooks-fetch-data
function PairwiseComparator() {
  const [models, setModels] = useState<ModelChoice>({ model1: "", model2: ""});
  const [modelChosen, setModelChosen] = useState("");
  useEffect(() => {
    let req = modelChosen == "" ? "choice" : "choice/" + modelChosen;
    async function fetchData() {
      const result = await axios.get<ModelChoice>(req)
      setModels(result.data);
    }
    fetchData();
    }, [modelChosen]);
  
  return (
    <div>
      <ModelView model={models.model1}/>
      <ModelView model={models.model2}/>
      <ButtonInterface label="model1" onClick = { () => {setModelChosen("1")} } />
      <ButtonInterface label="model2" onClick = { () => {setModelChosen("2")} } />
    </div>
  )
}

function ModelView(props) {
  return <p>I am a picture of model {props.model}</p>
}

function ButtonInterface(props) {
  return (
    <div>
      <button className="bg-green-500" onClick={() => props.onClick()}>
        {props.label}
      </button>
    </div>
  );
}

export default App;
