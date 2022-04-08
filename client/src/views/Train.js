import * as React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import BasicDatePicker from '../components/BasicDatePicker';
import BasicSelect from '../components/BasicSelect';
import defaults from '../defaults';
import { useNavigate } from "react-router-dom";
import './Train.css';

const PROVIDER = 'binance';

export default function Train() {
    const navigate = useNavigate();

    const [symbol, setSymbol] = React.useState([]);
    const [interval, _setInterval] = React.useState('1h');
    const [startDate, setStartDate] = React.useState('');
    const [endDate, setEndDate] = React.useState('');
    const [initialAmount, setInitialAmount] = React.useState(10000);
    const [numEpisodes, setNumEpisodes] = React.useState(1);

    async function trainAgent(config) {
        console.log('training agent with config: ');
        console.dir(config);
        const URL = '/api/train';
        return await fetch(URL, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
    }

    async function onTrainClick() {
        let config = {
            "provider": PROVIDER,
            "symbols": symbol,
            "interval": interval,
            "start_date": startDate,
            "end_date": endDate,
            "initial_amount": initialAmount,
            "n_episodes": numEpisodes,
            "commission": 0.00075
        }

        const agentRes = await fetch("/api/agent/create");
        agentRes.json().then( async res => {
            // update config with newly created agent
            let newAgentId = res.content.id;
            config.agent_id = newAgentId;

            // train new agent
            let trainedAgent = await trainAgent(config);
            trainedAgent.json().then( async () => {
                navigate("/");
            });
        });
    }

    function handleAssetSelect(e) {
        setSymbol(e.target.value);
    }
    
    function handleIntervalSelect(e) {
        _setInterval(e.target.value);
    }

    function handleStartSelect(formattedDate) {
        setStartDate(formattedDate);
    }

    function handleEndSelect(formattedDate) {
        setEndDate(formattedDate);
    }

    function handleAmountSelect(e) {
        setInitialAmount(e.target.value);
    }

    function handleEpisodeSelect(e) {
        setNumEpisodes(e.target.value);
    }

    return (
        <div className="train">
            <div className="main-space">
                <div className="box train-settings">
                    <div className="title">
                        <h2>Train Settings</h2>
                    </div>
                    <div className="settings">
                        <div className="group">
                            <BasicDatePicker label="Start Date" handleChange={handleStartSelect}/>
                            <BasicDatePicker label="End Date" handleChange={handleEndSelect} />
                        </div>
                        <div className="group">
                            <BasicSelect label="Interval" defaultValue={interval} options={defaults.intervals} handleChange={handleIntervalSelect} />
                            <TextField label="Initial Amount" value={initialAmount} onChange={handleAmountSelect} />
                            <TextField label="Episodes" value={numEpisodes} onChange={handleEpisodeSelect} />
                        </div>
                    </div>
                </div>
                <div className="box assets">
                    <div className="title">
                        <h2>Assets Manager</h2>
                    </div>
                </div>
            </div>
            <div className="box right-space">
                <div className="title">
                    <h2>Summary</h2>
                    <Button variant="contained" onClick={ onTrainClick }>Train</Button>
                </div>
            </div>
        </div>
    )
}
