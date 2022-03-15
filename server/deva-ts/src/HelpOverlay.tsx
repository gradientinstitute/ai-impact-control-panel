// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
import { atom, useRecoilState, useSetRecoilState, useRecoilValue} from 'recoil';
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';
import {Button, Tooltip, OverlayTrigger, CloseButton} from 'react-bootstrap';
import questionMark from './question-mark.svg';
import {Pane, paneState} from './Base';


export const helpState = atom({
  key: 'help',
  default: 0,
});

export enum overlayId {

  // Setup
  'ToggleHelp' = 1,
  'FilterStep',
  'Scenario',
  'Objectives',
  'Pipeline',
  'Remaining',
  'FilterPlot',
}

const overlayCfg = {
  [overlayId.ToggleHelp]: {
    message: "Tutorial help is enabled by default. Toggle it with this button, or click Next to get started!",
    placement: "bottom",
    lastInSection: false,
  },
  [overlayId.FilterStep]: {
    message: "This filter page allows you to remove some candidate models by imposing performance contraints. It helps reduce the number of questions you'll be asked in the subsequent elicitation step, which can also be configured below.",
    placement: "right",
    lastInSection: false,
  },
  [overlayId.Scenario]: {
    message: "These panes on the left provide an overview of the AI system for the decision makers. The information here would be collated by the organisation deploying the AI system",
    placement: "right",
    lastInSection: false,
  },
  [overlayId.Objectives]: {
    message: "These are the (qualitative) objectives of the system that the performance metrics try to capture",
    placement: "right",
    lastInSection: false,
  },
  [overlayId.Pipeline]: {
    message: "This is an overview of the system pipeline, from data to decision",
    placement: "right",
    lastInSection: false,
  },
  [overlayId.Remaining]: {
    message: "This pane shows the number of model candidates that are currently within the bounds set by the user below. These are a subset of all the candidates which would need to be supplied to the control panel by the data scientists building the system.",
    placement: "bottom",
    lastInSection: false,
  },
  [overlayId.FilterPlot]: {
    message: "This radar plot visualises the acceptable boundaries in terms of the best and worse values from amongst the candidate models.",
    placement: "bottom",
    lastInSection: false,
  }
}

// add a use effect that starts at a particular thing
export function HelpButton({}) {
  const [help, setHelpState] = useRecoilState(helpState);
  return(
    <div>
      <h2>Help state: {help}</h2>
      <HelpOverlay hid={overlayId.ToggleHelp}>
        <button className="col-span-1 px-2"
        onClick={() => { setHelpState(-1 * help) }}>
        <img className="col-span-1 h-6 right" src={questionMark}
          alt="Help" /> 
        </button>
      </HelpOverlay>
    </div>
  );
}

export function HelpOverlay({children, hid}) {
  
    const [ctr, setCtr] = useRecoilState(helpState);
    const pane = useRecoilValue(paneState);
    const cfg = overlayCfg[hid];

    if (cfg == null) {
      return (
        <Tooltip id={hid}>
          CFG UNDEFINED
          <br/><br/>
          <Button 
            variant="dark" 
            size="sm" 
            disabled={cfg.lastInSection} 
            onClick={()=>{setCtr(ctr + 1)}}>
              Next
          </Button>
        </Tooltip>
      );
    }

    const tooltip = (
      <Tooltip id={hid} className="">
          {cfg.message}
          <br/><br/>
        <Button 
          variant="dark" 
          size="sm" 
          disabled={cfg.lastInSection} 
          onClick={()=>{setCtr(ctr + 1)}}>
            Next
        </Button>
      </Tooltip>
    );
  
    return (
      <OverlayTrigger 
        show={ctr==hid}
        placement={cfg.placement} 
        overlay={tooltip}
      >
        {children}
      </OverlayTrigger>
  
    );
  }
  
