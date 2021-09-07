import React, {useState, useEffect} from 'react';
import axios from 'axios';
import './App.css';

function App() {
  return (
    <div className="App container mx-auto text-center">
          <h1 className="pb-8">AI Governance Control Panel</h1>
          <PairwiseComparator />
    </div>
  );
}

// https://codesandbox.io/s/jvvkoo8pq3?file=/src/index.js
// https://www.robinwieruch.de/react-hooks-fetch-data
// https://dmitripavlutin.com/react-useeffect-infinite-loop/
function PairwiseComparator() {
  const [model1, setModel1] = useState<any>(null);
  const [model2, setModel2] = useState<any>(null);
  const [model1Name, setModel1Name] = useState("loading");
  const [model2Name, setModel2Name] = useState("loading");
  const [modelChosen, setModelChosen] = useState("");
  const [stage, setStage] = useState(1);

  // initial request on load
  useEffect(() => {
    let req = "choice";
    async function fetchData() {
      const result = await axios.get<any>(req);
      setModel1(result.data.model1);
      setModel2(result.data.model2);
    }
    fetchData();
    }, []
  );

  //Update model names on request coming back
  useEffect(() => {
    if (model1 !== null) {
      setModel1Name(model1.name);
    }
    if (model2 !== null) {
      setModel2Name(model2.name);
    }
  }, [model1, model2]);
  
  // request on button push
  useEffect(() => {
    let req = "choice/" + stage + "/" + modelChosen;
    async function fetchData() {
      const result = await axios.get<any>(req);
      setModel1(result.data.model1);
      setModel2(result.data.model2);
    }
    if (modelChosen !== "") {
      fetchData();
      setModelChosen("");
      setStage(stage => stage + 1);
    }
    }, [modelChosen]
  );
  
  return (
    <div className="flex flex-row gap-5">
      <div className="flex-1 space-y-5">
        <ModelView model={model1}/>
        <ButtonInterface label={model1Name} onClick = { () => { setModelChosen("1") } } />
      </div>
      <div className="flex-1 space-y-5">
        <ModelView model={model2}/>
        <ButtonInterface label={model2Name} onClick = { () => { setModelChosen("2") } } />
      </div>
    </div>
  )
}

function ModelView(props) {
  return (
    <div className="h-48 bg-gray-50 flex flex-wrap content-center justify-center">
      <div>
      <p>I am a picture of model {JSON.stringify(props.model)}</p>
      </div>
    </div>
    )
}

function ButtonInterface(props) {
  return (
    <div>
      <button className="bg-green-500 rounded-lg" onClick={() => props.onClick()}>
        <div className="p-4">
          {props.label}
        </div>
      </button>
    </div>
  );
}

export default App;
