import React, {useState, useEffect} from 'react';
import {RecoilRoot, useRecoilValue} from 'recoil';
import {Pane, paneState} from './Base';
import {PairwisePane} from './Pairwise';
import {IntroPane} from './Intro';
import {ResultPane} from './Result';
import {SetupPane} from './Setup';
import {ConstraintPane} from './Constrain';
import './App.css';
import logo from './logo-dark-small.svg';



function App() {

  return (
    <RecoilRoot>
    <div className="App container text-gray-200 mx-auto mb-32 px-8 pt-8 bg-gray-800">
      <div className="grid grid-cols-12 text-center items-center mb-8">
        <img className="col-span-2 h-16" src={logo} alt="Gradient Institute logo" />
        <h1 className="col-span-8 text-3xl">AI Impact Governance Software</h1>
        <div className="col-span-2" />
      </div>
      <Content />
    </div>
    </RecoilRoot>
  );
}

function Content() {

  const pane = useRecoilValue(paneState);

  let content = {};
  content[Pane.Setup] = (<SetupPane />);
  content[Pane.Intro] = (<IntroPane />);
  content[Pane.Constrain] = (<ConstraintPane />);
  content[Pane.Pairwise] = ( <PairwisePane />);
  content[Pane.Result] = (<ResultPane />);

  return (
    <div>
      {content[pane]}
    </div>
  );

}

export default App;
