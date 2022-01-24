import * as React from 'react';
import Train from './views/Train';
import Test from './views/Test';
import Loading from './views/Loading';
import './App.css';
import config from './config';



function App() {
    const [loading, setLoading] = React.useState(false);
    const [evaluation, setEvaluation] = React.useState(false);
    const [results, setResults] = React.useState(null);

    function onTrainClick() {
        setLoading(true);
    }

    function onTrainEnd(res) {
        setLoading(false);
        setEvaluation(true);
        // setResults(res);
    }

    return (
    <div className="App">
        { !evaluation ?
            !loading ?
                <Train config={config} 
                    onTrainClick={onTrainClick}
                    onTrainEnd={onTrainEnd} /> :
                <Loading /> :
            <Test results={results} />
        }
    </div>
    );
}

export default App;
