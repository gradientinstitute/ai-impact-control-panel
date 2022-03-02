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
  'Scenario',
}

const overlayCfg = {
  [overlayId.ToggleHelp]: {
    message: "Tutorial help is enabled by default. Toggle it with this button, or click Next to get started!",
    placement: "bottom",
    lastInSection: false,
  },
  [overlayId.Scenario]: {
    message: "These panes on the left provide an overview of the AI system for the decision makers. The information here would be collated by the organisation deploying the AI system",
    placement: "right",
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
  
