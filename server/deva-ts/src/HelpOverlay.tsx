import { atom, useRecoilState, useSetRecoilState, useRecoilValue} from 'recoil';
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';
import {Popover, Button, Tooltip, OverlayTrigger, CloseButton} from 'react-bootstrap';
import questionMark from './question-mark.svg';

export const helpState = atom({
  key: 'help',
  default: 0,
});

export enum overlayRank {

  // Setup Panel
  'Boundaries' = 1, // initialise to 1 so we can multiply by -1 to close
  'Deployment',

  // Setup Panel (continued)
  'Name',
  'Scenario',

  // Constraint Panel
  'ScenarioDetails',
  'ScenarioObjectives',
  'ScenarioPipeline',
  'CandidatesRemaining',
  'ConstraintScrollbars',
  'ElicitationSettings',

  // Pairwise Panel
  'Motivation',
  // 'PairwiseComparisons',
  // 'Preference',

  // Final Panel
  'Results',
  'DownloadSessionLog',
}

// add a use effect that starts at a particular thing
export function HelpButton({}) {
  const [help, setHelpState] = useRecoilState(helpState);
  
  return(
    <button className="col-span-1 px-2"
    onClick={() => {
      setHelpState(help * -1);
    }}>
    <img className="col-span-1 h-6 right" src={questionMark}
      alt="Help" /> 
    </button>
  );
}

export function HelpOverlay({children, rank, title, msg, placement}) {
  
    const [ctr, setCtr] = useRecoilState(helpState);
  
    const popover = (
      <Popover id={rank} className="bg-gray-700 border-gray-500 shadow-sm bg-opacity-90 hover:bg-opacity-100">
        <Popover.Header as="h3" className="text-white border-gray-500 bg-gray-800 bg-opacity-90">
          {title}        
          <button className="col-span-1" onClick={() => setCtr(ctr * -1)}>
            &times;
          </button>
        </Popover.Header>
        <Popover.Body className="text-white">
          {msg}
          <br/><br/>
          <Button variant="dark" size="sm" 
            onClick={()=>{setCtr(ctr - 1)}}>&lt;</Button>
          <Button variant="dark" size="sm" 
            onClick={()=>{setCtr(ctr + 1)}}>&gt;</Button>
        </Popover.Body>
      </Popover>
    );
  
    return (
      <OverlayTrigger 
        show={ctr==rank}
        placement={placement} 
        overlay={popover}
      >
        {children}
      </OverlayTrigger>
  
    );
  }
  