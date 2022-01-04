import {atom} from 'recoil';

// what pane are we looking at
export enum Pane {
  Setup,
  Intro,
  Constrain,
  Pairwise,
  Result,
}

// this global state is only for items that need to persist across panes

// state for the current pane
export const paneState = atom({  
  key: 'pane', 
  default: Pane.Setup, // default value (aka initial value)
});

// state for which scenario has been chosen by the user
export const scenarioState = atom({  
  key: 'scenario', 
  default: null, 
});

// state for which algorithm has been chosen by the user
export const algoState = atom({  
    key: 'algorithm', 
    default: null, 
  });

// state for name entered by the user
export const nameState = atom({  
  key: 'name', 
  default: null, 
});

// state for the metadata for the chosen scenario
// for the scenario & algo
export const metadataState = atom({  
  key: 'metadata', 
  default: null, 
});

// the contraints selected by the user
export const constraintsState = atom({  
  key: 'constraints', 
  default: null, 
});


// state for the result of the deployment elicitation
export const resultState = atom({  
  key: 'result', 
  default: null, 
});

