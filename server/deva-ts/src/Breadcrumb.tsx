// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
import {useRecoilValue} from 'recoil';

import {Pane, paneState} from './Base';
import './Breadcrumb.css';

export function Breadcrumb() {
  const pane = useRecoilValue(paneState);

  const STEPS = {
    Intro: {label: 'Configure'},
    Pairwise: {label: 'Preference Selection'},
    Result: {label: 'Results'}
  }

  return (
    <div className="col-span-12">
      <ol className="breadcrumb">
      { Object.entries(STEPS).map(([name, value]) => 
        <li key={name} className="mr-6" data-selected={Pane[pane] === name}>
          {value.label}
        </li>
        )}
      </ol>
    </div>
  )
}
