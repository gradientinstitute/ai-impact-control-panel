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
  'UnitFilter',
  'UnitDescription',
  'UnitFilterWords',
  'UnitFilterMin',
  'UnitFilterRange',
  'UnitFilterMax',
  'Algorithm',
  'LastOnConfig',
  'FirstOnPairwise',
  'PairwiseRadar',
  'PairwiseButton',
  'PairwiseText',
  'PairwiseDetail',
  'PairwiseAbsolute',
  'PairwiseRelative',
  'Important',
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
  },
  [overlayId.UnitFilter]: {
    message: "There is one of these boxes for each metric.",
    placement: "bottom",
    lastInSection: false,
  },
  [overlayId.UnitDescription]: {
    message: "This describes the performance metric, including the objective it captures and any limitations in its measurement.",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.UnitFilterWords]: {
    message: "This sentence gives the current range of values for the metric accepted by the filter", 
    placement: "top",
    lastInSection: false,
  },
  [overlayId.UnitFilterMin]: {
    message: "This is the minimum value of the metric over all the candidates",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.UnitFilterRange]: {
    message: "Adjust this slider to tighten or loosen the candidate filter",
    placement: "bottom",
    lastInSection: false,
  },
  [overlayId.UnitFilterMax]: {
    message: "This is the maximum value of the metric over all the candidates",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.Algorithm]: {
    message: "The settings for the elicitation process used on the remaining candidates are given here",
    placement: "top",
    lastInSection: true,
  },
  [overlayId.FirstOnPairwise]: {
    message: "This next stage of the tool asks a series of questions comparing two different candidates in order to find the most preferred one to deploy",
    placement: "bottom",
    lastInSection: false,
  },
  [overlayId.PairwiseRadar]: {
    message: "The radar plots gives a visual indication of the two candidates' relative performance",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.PairwiseButton]: {
    message: "Clicking on the left or right button tells the algorithm which system you prefer",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.PairwiseText]: {
    message: "For record-keeping, you can describe what motivated your choice here with some text",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.PairwiseDetail]: {
    message: "These boxes give more detailed information about the relative and absolute performance of the systems against each metric",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.PairwiseAbsolute]: {
    message: "This section describes the absolute performance of the model with respect to each metric",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.PairwiseRelative]: {
    message: "This section compares their performance",
    placement: "top",
    lastInSection: false,
  },
  [overlayId.Important]: {
    message: "For record-keeping, you can mark which metrics were important for your choice",
    placement: "top",
    lastInSection: true,
  },
}

// add a use effect that starts at a particular thing
export function HelpButton({}) {
  const [help, setHelpState] = useRecoilState(helpState);
  return(
    <div>
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
    
    if (!(hid in overlayCfg)) {
      return children;
    }

    const cfg = overlayCfg[hid];
    const buttonText = cfg.lastInSection ? "Close" : "Next";

    const tooltip = (
      <Tooltip id={hid} className="">
          {cfg.message}
          <br/><br/>
        <Button 
          variant="dark" 
          size="sm" 
          onClick={()=>{setCtr(ctr + 1)}}>
            {buttonText}
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
  
