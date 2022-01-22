import * as React from 'react';
import Train from './views/Train';
import Test from './views/Test';
import Loading from './views/Loading';
import './App.css';
import config from './config';



function App() {
    const [loading, setLoading] = React.useState(false);
    const [evaluation, setEvaluation] = React.useState(false);

    return (
    <div className="App">
        { !evaluation ?
            !loading ?
                <Train config={config} /> :
                <Loading /> :
            <Test />
        }
    </div>
    );
}

export default App;
