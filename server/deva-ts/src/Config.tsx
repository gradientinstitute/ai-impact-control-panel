import _ from "lodash";

import { useEffect, useState } from 'react';
import { atom, useRecoilState, useRecoilValue } from 'recoil';
import { configState } from './Base';
import cog from './cog.svg';

import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';
import NativeSelect from '@mui/material/NativeSelect';

import { Dialog } from "@reach/dialog";
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';

const showConfigState = atom({
  key: 'showConfig',
  default: false,
});

export function ConfigPanel({}) {
  
  const [configs, setConfigs] = useRecoilState(configState);
  const [showConfig, setShowConfig] = useRecoilState(showConfigState);

  // initial loading of config
  useEffect(() => {
    // placeholder configurations
    var configs = {
      displaySpiderPlot : {
        'options' : ["true", "false"],
        'selected' : "true", // default
      },
      scrollbarDisplay : {
        'options' : ['most optimal on left', 'lower value on left', 'something else on left'],
        'selected' : 'lower value on left'
      }
    }
    setConfigs(configs);
  }, []);

  const panel = (
    <div className="ml-auto mr-auto w-1/2">
      <Dialog className="intro text-center" aria-label="Settings" >
        <div className="grid-cols-12 text-right items-right mb-8 ">
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

  const [configs, setConfigs] = useRecoilState(configState);
  const configList = _.mapValues(configs, (val, _obj) => {
    const options = val.options;
    const selected = val.selected;
    return {options, selected};
  });

  console.log(configList)

  const dropdowns = Object.entries(configList).map(([config, choices]) => {
    return (
      <div>
      <DropdownButton config ={config} selected={choices.selected} options={choices.options}/>
      <div className="h-5"></div>
      </div>
    );
  })

  return (
    <div className="p-4 gap-4 grid grid-cols-10">
      <div className="col-span-2"/>   
      <div className="col-span-6">
        {dropdowns}
      </div>
      <div className="col-span-2"/>
    </div>
  );
}

function DropdownButton({config, selected, options}) {

  const [configs, setConfigs] = useRecoilState(configState);
  const mappedItems = (Object.values(options)).map((val) => {
    const v = val as string;
    return (
      <option value={v}>{v}</option>
    );
  });

  function handleChange(event) {
    let updatedConfigs = _.mapValues(configs, x => { return x });    
    const newConfig = {
      'options' : configs[config]['options'],
      'selected': event.target.value
    };
    updatedConfigs[config] = newConfig;
    setConfigs(updatedConfigs);
  }

  return (
    <div>
    <Box sx={{ minWidth: 120}}>
    <FormControl fullWidth>
      <InputLabel variant="standard" htmlFor="uncontrolled-native" sx={{ color: "white"}}>
        {config}
      </InputLabel>
      <NativeSelect
        defaultValue={selected as string}
        inputProps={{
          name: config as string,
          id: config as string,
        }}
        sx={{ color: "gray"}}
        onChange={event => handleChange(event)}
      >
      {mappedItems}
    </NativeSelect>
    </FormControl>
    </Box>
    </div>
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
