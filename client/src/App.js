import * as React from 'react';
import { Routes, Route, Link } from "react-router-dom";
import Train from './views/Train';
import Test from './views/Test';
import Agents from './views/Agents';
import './App.css';


function App() {
    return (
    <div className="App">
        <Routes>
            <Route path="/" element={ <Agents /> } />
            <Route path="/train" element={ <Train /> } />
            <Route path="/test/:agentId" element={ <Test /> } />
        </Routes>
    </div>
    );
}

export default App;
