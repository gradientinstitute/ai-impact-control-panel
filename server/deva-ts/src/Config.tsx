import axios from 'axios';
import _ from "lodash";

import { useEffect } from 'react';
import { atom, useRecoilState } from 'recoil';
import { configState } from './Base';
import cog from './cog.svg';

import { Dialog } from "@reach/dialog";
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';

const showConfigState = atom({
  key: 'showConfig',
  default: false,
});

export function ConfigPanel({}) {
  
  const [config, setConfig] = useRecoilState(configState);
  const [showConfig, setShowConfig] = useRecoilState(showConfigState);

  // initial loading of config
  useEffect(() => {
    // placeholder configurations
    const enabled = true;
    const config = {
      config1 : enabled,
      config2 : !enabled,
    }
    setConfig(config);
  }, []);
  
  const panel = (
    <div className="ml-auto mr-auto w-1/2">
      <Dialog className="intro text-center" aria-label="Settings">
        <div className="grid-cols-12 text-right items-right mb-8">
          <div className="col-span-11"/>
          <button className="col-span-1"
            onClick={() => setShowConfig(false)}>&times;
          </button>
          <h1 className="font-extralight mb-4 text-3xl pb-4">Settings</h1>
        </div>
        
        {JSON.stringify(config)}
      </Dialog>
    </div>  
  );

  return showConfig ? panel : null;
}

export function ConfigButton({}) {
  const [showConfig, setShowConfig] = useRecoilState(showConfigState);
  return(
    <button className="col-span-1"
    onClick={() => setShowConfig(true)}>
    <img className="col-span-1 h-6 right" src={cog}
      alt="Settings" /> 
    </button>
  );
}
