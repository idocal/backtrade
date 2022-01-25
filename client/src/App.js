import * as React from 'react';
import ConfigModal from './views/ConfigModal';
import Test from './views/Test';
import Loading from './views/Loading';
import './App.css';
import config from './config';


function App() {
    const [mode, setMode] = React.useState('train');
    const [loading, setLoading] = React.useState(false);
    const [evaluation, setEvaluation] = React.useState(false);
    const [results, setResults] = React.useState(null);
    const [loadingStatus, setLoadingStatus] = React.useState(0);

    function onTrainClick() {
        setLoading(true);
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
                    mode={mode}
                    onTrainClick={onTrainClick}
                    onTrainEnd={onTrainEnd}
                    onTestClick={onTestClick}
                    onTestEnd={onTestEnd}
                    setLoadingStatus={setLoadingStatus} /> :
                <Loading percentage={loadingStatus} /> :
            <Test results={results} />
        }
    </div>
    );
}

export default App;
