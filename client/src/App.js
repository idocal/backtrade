import * as React from 'react';
import ConfigModal from './views/ConfigModal';
import Evaluation from './views/Evaluation';
import Loading from './views/Loading';
import './App.css';
import config from './config';


function App() {
    const [mode, setMode] = React.useState('train');
    const [loading, setLoading] = React.useState(false);
    const [evaluation, setEvaluation] = React.useState(false);
    const [results, setResults] = React.useState(null);
    const [loadingStatus, setLoadingStatus] = React.useState(0);
    const [agentId, setAgentId] = React.useState('');

    function onTrainClick(newAgentId) {
        setLoading(true);
        setAgentId(newAgentId);
    }

    function onTrainEnd() {
        setMode('test');
        setLoading(false);
    }

    function onTestClick() {
        setLoading(true);
    }

    function onTestEnd(res) {
        setLoading(false);
        setResults(res);
        setEvaluation(true);
    }

    return (
    <div className="App">
        { !evaluation ?
            !loading ?
                <ConfigModal config={config} 
                    agentId={agentId}
                    mode={mode}
                    onTrainClick={onTrainClick}
                    onTrainEnd={onTrainEnd}
                    onTestClick={onTestClick}
                    onTestEnd={onTestEnd}
                    setLoadingStatus={setLoadingStatus} /> :
                <Loading percentage={loadingStatus} /> :
            <Evaluation results={results} />
        }
    </div>
    );
}

export default App;
