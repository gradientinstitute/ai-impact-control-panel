import {RecoilRoot, useRecoilValue} from 'recoil';

import {Pane, paneState} from './Base';
import {PairwisePane} from './Pairwise';
import {ResultPane} from './Result';
import {SetupPane} from './Setup';
import {ConfigurePane} from './Configure';
import {BoundariesPane} from './Boundaries';
import {ConfigButton, ConfigPanel} from './Config';
import {HelpButton} from './HelpOverlay';
import {ReportPane} from './Report';
import {UserReportPane} from './ConstrainReport';
import {Breadcrumb} from './Breadcrumb';

import './App.css';
import logo from './logo-dark-small.svg';


function App() {
  return (
    <RecoilRoot>
      <div className="App container text-gray-200 mx-auto mb-32
        px-8 pt-8 bg-gray-800">
        <div className="grid grid-cols-12 text-center items-center mb-8">
          <img className="col-span-2 h-16" src={logo}
            alt="Gradient Institute logo" />
          <h1 className="col-span-8 text-3xl">AI Impact Control Panel</h1>
          <div className="col-span-2">
            <HelpButton />
            <ConfigButton />
          </div>
          <Breadcrumb />
        </div>
        <Content />
        <ConfigPanel />
      </div>
    </RecoilRoot>
  );
}


// the root react component: the whole ui sit under this
function Content() {

  const pane = useRecoilValue(paneState);

  let content = {};
  content[Pane.Setup] = (<SetupPane />);
  content[Pane.Configure] = (<ConfigurePane />)
  content[Pane.Pairwise] = ( <PairwisePane />);
  content[Pane.Result] = (<ResultPane />);
  content[Pane.Boundaries] = (<BoundariesPane />);
  content[Pane.Report] = (<ReportPane />);
  content[Pane.UserReport] = (<UserReportPane />);

  return (
    <div>
      {content[pane]}
    </div>
  );

}

export default App;
