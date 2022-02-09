import {useState, useEffect} from 'react';
import axios from 'axios';

import { useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil';
import { Pane, paneState, scenarioState, constraintsState, TaskTypes, taskTypeState } from './Base';


export function ReportPane({}) {
  const scenario = useRecoilValue(scenarioState);
  const constraints = useRecoilValue(constraintsState);

  // useEffect(() => {
    // const fetch = async () => {
    //   const result = await axios.put<any>("api/" + scenario + "/bounds/save", constraints);
    //   const d = result.data;
    //   return d
    // }
  //   fetch();
  // }, []
  // );

  const result = axios.put<any>("api/" + scenario + "/bounds/save", constraints);
  const d = result[2];


  console.log(d)

  return (
    <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-10 grid-cols-1 text-center items-center pb-10">
      <h1>Results Placeholder</h1>
      Your content here.
      for each REFERENCE (eg inaction, industry avg), report whether they meet the current bounds,
      and if they don't, identify why not (eg "inaction: true positive rate is too low")


      <div className="width-1/4">
        <BackButton />
      </div>
      <div className="width-1/4">
        <CompleteButton
        constraints={constraints}
        scenario={scenario} />
      </div>
    </div>
  );
}

function CompleteButton({scenario, constraints}) {

  const [submit, setSubmit] = useState(false);

  // const scenario = useRecoilValue(scenarioState);
  // const constraints = useRecoilValue(constraintsState);

  useEffect(() => {
    const fetch = async () => {
      await axios.put<any>("api/" + scenario + "/bounds/save", constraints);
      window.location.href='/';
    }
    if (submit) {
      fetch();
    }
  }, [submit]
  );

  return (
    <button className="bg-gray-200 text-black rounded-lg" 
      onClick={() => {setSubmit(true)}}>
      <div className="p-4 text-5xl">
        Complete
      </div>
    </button>
  );
}


// TODO: Back button
// Need to be fixed
function BackButton({}) {
  const [_pane, setPane] = useRecoilState(paneState);
  return (
  <div className="flex flex-1 align-middle text-left">
    <button className="hover:text-gray-400 transition"
      onClick={() => setPane(Pane.Boundaries)}>
      <div className="p-4 text-3xl">
        &#8249; Back
      </div>
    </button>
  </div>
  );
}
