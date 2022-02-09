import _ from "lodash";

import { useEffect } from 'react';
import { atom, useRecoilState, useRecoilValue } from 'recoil';
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
  
  const [_config, setConfig] = useRecoilState(configState);
  const [showConfig, setShowConfig] = useRecoilState(showConfigState);

  // initial loading of config
  useEffect(() => {
    // placeholder configurations
    const config = {
      displaySpiderPlot : {
        'options' : ["true", "false"],
        'selected' : "true", // default
      },
      scrollbarDisplay : {
        'options' : ['most optimal on left', 'lower value on left', 'third option'],
        'selected' : 'lower value on left'
      }
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
        <DisplayOptions/>
      </Dialog>
    </div>  
  );

  return showConfig ? panel : null;
}

function DisplayOptions({}) {

  const config = useRecoilValue(configState);
  const configList = _.mapValues(config, (val, _obj) => {
    const options = val.options
    const selected = val.selected
    return {options, selected};
  });

  const dropdowns = Object.values(configList).map((choices) => {
    return (
      <div>
      <DropdownButton selected={choices.selected} options={choices.options}/>
      </div>
    );
  })

  const configs = Object.entries(configList).map(([config, choices]) => {
    return (
      <p className="text-right">{config}</p>
    );
  });

  return (
    <div className="p-4 gap-4 grid grid-cols-10" >
      <div className="col-span-1"/>
      <div className="col-span-3">
        {configs}
      </div>     
      <div className="col-span-4">
        {dropdowns}
      </div>
      <div className="col-span-1"/>
    </div>
  );
}

function DropdownButton({selected, options}) {
  options = ([...options]).filter(x => x != selected);
  const mappedItems = options.map((val) => {
    return (
      <option value={val as string}>{val}</option>
    );
  });

  return(
    <select className="form-select">
      <option selected>{selected}</option>
      {mappedItems}
    </select>
  );
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
