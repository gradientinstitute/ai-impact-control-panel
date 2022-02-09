import {useState, useEffect} from 'react';
import axios from 'axios';

import { useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil';
import { Pane, paneState, scenarioState, constraintsState, TaskTypes, taskTypeState } from './Base';


export function ReportPane({}) {

    return (
      <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-10 grid-cols-1 text-center items-center pb-10">
        <h1>Results Placeholder</h1>
        Your content here.
        <div className="width-1/4">
          <BackButton />
        </div>
        <div className="width-1/4">
          <CompleteButton />
        </div>
      </div>
    );
  }

  function CompleteButton({}) {

    const [submit, setSubmit] = useState(false);
  
    const scenario = useRecoilValue(scenarioState);
    const constraints = useRecoilValue(constraintsState);
  
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
  // function BackButton({}) {

  //   const [submit, setSubmit] = useState(false);
  
  //   const scenario = useRecoilValue(scenarioState);
  //   const constraints = useRecoilValue(constraintsState);
  
  //   const [_pane, setPane] = useRecoilState(paneState);
  
  //   useEffect(() => {
  //     const fetch = async () => {
  //       await axios.put<any>("api/" + scenario + "/bounds/save", constraints);
  //       // window.location.href='/';
  //       setPane(Pane.Boundaries)
  //     }
  //     if (submit) {
  //       fetch();
  //     }
  //   }, [submit]
  //   );
  
  //   return (
  //       <button className="bg-gray-200 text-black rounded-lg" 
  //         onClick={() => {setSubmit(true)}}>
  //         <div className="p-4 text-5xl">
  //           Back
  //         </div>
  //       </button>
  //   );
  // }

// Need to be fixed
function BackButton({}) {
  const setTask = useSetRecoilState(taskTypeState);
  
  const [_pane, setPane] = useRecoilState(paneState);
  return (
    <button className="btn text-2xl uppercase py-8 font-bold rounded-lg"
      onClick={() => {
        setTask(TaskTypes.Boundaries);
        // setTabIndex(1);
        setPane(Pane.Boundaries)
      }}>
        Back
    </button>
  );
}
