import { atom, useRecoilState, useSetRecoilState, useRecoilValue} from 'recoil';
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';
import {Popover, Button, Tooltip, OverlayTrigger, CloseButton} from 'react-bootstrap';
import questionMark from './question-mark.svg';
import {Pane, paneState} from './Base';

export const setupTabIndexState = atom({
  key: 'setupTabIndex',
  default: 0,
});

export const helpState = atom({
  key: 'help',
  default: 0,
});

export function getOverlayBoundary(pane, setupTabIndex=0) {

  let start = -1;
  let end = -1;

  // if (disableHelp == true) {
  //   return {start, end};
  // }

  switch (pane) {
    case Pane.Setup: {
      start = (setupTabIndex == 0) ? overlayRank.Boundaries : overlayRank.Name;
      end = (setupTabIndex == 0) ? overlayRank.Deployment : overlayRank.Scenario;
      break;
    }
    case Pane.Configure: {
      start = overlayRank.ScenarioDetails;
      end = overlayRank.ElicitationSettings;
      break;
    }
    case Pane.Pairwise: {
      start = overlayRank.Motivation;
      end = overlayRank.Motivation;
      break;
    }
    case Pane.Result: {
      start = overlayRank.Results;
      end = overlayRank.DownloadSessionLog;
      break;
    }
  }

  return {start, end};
}

export enum overlayRank {

  // Setup
  'Boundaries',
  'Deployment',
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
  const pane = useRecoilValue(paneState);
  const setupTabIndex = useRecoilValue(setupTabIndexState);
  const state = getOverlayBoundary(pane, setupTabIndex).start;
  
  function toggleHelp(help) {
    if (help > 0) {
      setHelpState(-1);
    } else {
      setHelpState(state);
    }
  }

  return(
    <button className="col-span-1 px-2"
    onClick={() => { toggleHelp(help) }}>
    <img className="col-span-1 h-6 right" src={questionMark}
      alt="Help" /> 
    </button>
  );
}

export function HelpOverlay({children, rank, title, msg, placement}) {
  
    const [ctr, setCtr] = useRecoilState(helpState);
    const pane = useRecoilValue(paneState);
    const setupTabIndex = useRecoilValue(setupTabIndexState);
    const boundary = getOverlayBoundary(pane, setupTabIndex);
  
    const disableForward = ((ctr + 1) > boundary.end);
    const disableBackward = ((ctr - 1) < boundary.start);
  
    const backButton = disableBackward
      ? <Button variant="dark" size="sm" disabled onClick={()=>{setCtr(ctr - 1)}}>&lt;</Button>
      : <Button variant="dark" size="sm" onClick={()=>{setCtr(ctr - 1)}}>&lt;</Button>;

    const forwardButton = disableForward
      ? <Button variant="dark" size="sm" disabled onClick={()=>{setCtr(ctr + 1)}}>&gt;</Button>
      : <Button variant="dark" size="sm" onClick={()=>{setCtr(ctr + 1)}}>&gt;</Button>;
      
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
          {backButton}
          {forwardButton}
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
  