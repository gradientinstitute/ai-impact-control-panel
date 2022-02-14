import {atom} from 'recoil';

// what pane are we looking at
export enum Pane {
  Setup,
  Configure,
  Pairwise,
  Result,
  Boundaries, // new one for boundary scroll bars
  Report  // new one for display bounds configurations
}

export enum TaskTypes {
  Boundaries,
  Deployment,
}

// this global state is only for items that need to persist across panes

// state for the current pane
export const paneState = atom({  
  key: 'pane', 
  default: Pane.Setup, // default value (aka initial value)
});

// Which type of problem the user has chosen to elicit
export const taskTypeState = atom({
    key: 'taskType',
    default: null,
  });


// the set of algorithms retrieved from the serever
export const algoChoicesState = atom({
    key: 'algorithmChoices',
    default: [],
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
  default: "", 
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


// state for the report of the boundaries condfigurations
export const reportState = atom({  
    key: 'report', 
    default: null, 
  });

// state for configurations
export const configState = atom({
  key: 'config',
  default: null, 
});
