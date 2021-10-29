import {atom} from 'recoil';

export enum Pane {
  Setup,
  Intro,
  Constrain,
  Pairwise,
  Result,
}

export const paneState = atom({  
  key: 'pane', 
  default: Pane.Setup, // default value (aka initial value)
});

export const metadataState = atom({  
  key: 'metadata', 
  default: null, 
});

export const resultState = atom({  
  key: 'result', 
  default: null, 
});

export const scenarioState = atom({  
  key: 'scenario', 
  default: null, 
});

