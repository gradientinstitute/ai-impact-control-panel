import { useEffect, useState } from 'react';
import { atom, useRecoilState, useSetRecoilState, useRecoilValue} from 'recoil';
import axios from 'axios';
import { Dialog } from "@reach/dialog";
import { Tabs, TabList, Tab, TabPanels, TabPanel, TabsOrientation } from "@reach/tabs";
import "@reach/tabs/styles.css";
import "@reach/dialog/styles.css";
import './Setup.css';
import {Popover, Button, Tooltip, OverlayTrigger, CloseButton} from 'react-bootstrap';
import questionMark from './question-mark.svg';

// the set of scenarios retrieved from the server
export const helpState = atom({
  key: 'help',
  default: 0,
});

export enum overlayRankSetup {
  'Boundaries',
  'Deployment',
}

export function HelpButton({}) {
  const [help, setHelpState] = useRecoilState(helpState);
  return(
    <button className="col-span-1 px-2"
    onClick={() => {
      const helpTarget = help == -1 ? 0 : -1;
      setHelpState(helpTarget)
    }}>
    <img className="col-span-1 h-6 right" src={questionMark}
      alt="Help" /> 
    </button>
  );
}

export function HelpOverlay({children, rank, title, msg, placement}) {
  
    const [ctr, setCtr] = useRecoilState(helpState);
  
    const popover = (
      <Popover id={rank}>
        <Popover.Header as="h3">
          {title}
        <CloseButton onClick={() => setCtr(-1)}/>
        </Popover.Header>
        <Popover.Body>
          {msg}
          <div>
            <br/>
          <Button variant='primary' onClick={()=>{setCtr(ctr - 1)}}>Previous</Button>
          <Button variant='secondary' onClick={()=>{setCtr(ctr + 1)}}>Next</Button>
          </div>
        </Popover.Body>
      </Popover>
    )
  
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
  