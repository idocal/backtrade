import * as React from 'react';
import { Routes, Route, Link } from "react-router-dom";
import Train from './views/Train';
import Test from './views/Test';
import Dashboard from './views/Dashboard';
import Agents from './views/Agents';
import Header from './views/Header';
import Navbar from './views/Navbar';
import './App.css';


function App() {
    return (
    <div className="App">
        <Header />
        <div className="site">
            <Navbar />
            <Routes>
                <Route exact path="/" element={ <Dashboard /> } />
                <Route path="/train" element={ <Train /> } />
                <Route path="/test/:agentId" element={ <Test /> } />
            </Routes>
        </div>
    </div>
    );
}

export default App;
