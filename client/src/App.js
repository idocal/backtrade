import * as React from 'react';
import { Routes, Route, Link } from "react-router-dom";
import Train from './views/Train';
import Test from './views/Test';
import Agents from './views/Agents';
import './App.css';


function App() {
    const [agents, setAgents] = React.useState([]);

    function addAgent(agentId) {
        let newAgents = agents.push(agentId);
        setAgents(newAgents);
    }

    return (
    <div className="App">
        <Routes>
            <Route path="/" element={ <Agents agents={agents} /> } />
            <Route path="/train" element={ <Train addAgent={addAgent} /> } />
            <Route path="/test/:agentId" element={ <Test /> } />
        </Routes>
    </div>
    );
}

export default App;
