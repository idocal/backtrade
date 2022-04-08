import * as React from 'react';
import _ from 'lodash';
import { isValid, format } from 'date-fns';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import BasicDatePicker from '../components/BasicDatePicker';
import BasicSelect from '../components/BasicSelect';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import defaults from '../defaults';
import { useNavigate } from "react-router-dom";
import './Train.css';

const PROVIDER = 'binance';

export default function Train() {
    const navigate = useNavigate();

    const [interval, _setInterval] = React.useState('1h');
    const [startDate, setStartDate] = React.useState(new Date('2019-01-01T00:00:00'));
    const [endDate, setEndDate] = React.useState(new Date('2020-01-01T00:00:00'));
    const [initialAmount, setInitialAmount] = React.useState(10000);
    const [numEpisodes, setNumEpisodes] = React.useState(1);
    const [checkedAssets, setCheckedAssets] = React.useState(["BTC", "ETH"]);

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
        let formattedStartDate;
        let formattedEndDate;
        if (isValid(startDate)) {
            formattedStartDate = format(startDate, "yyyy-MM-dd");
        }
        if (isValid(endDate)) {
            formattedEndDate = format(endDate, "yyyy-MM-dd");
        }
        let config = {
            "provider": PROVIDER,
            "symbols": checkedAssets,
            "interval": interval,
            "start_date": formattedStartDate,
            "end_date": formattedEndDate,
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

    function handleIntervalSelect(e) {
        _setInterval(e.target.value);
    }

    function handleStartSelect(date) {
        setStartDate(date);
    }

    function handleEndSelect(date) {
        setEndDate(date);
    }

    function handleAmountSelect(e) {
        setInitialAmount(e.target.value);
    }

    function handleEpisodeSelect(e) {
        setNumEpisodes(e.target.value);
    }

    function checkAsset(asset) {
        let assetIndex = checkedAssets.indexOf(asset);
        if (assetIndex < 0) {
            setCheckedAssets([...checkedAssets, asset]);
        } else {
            let tmpAssets = [...checkedAssets]
            _.pull(tmpAssets, asset);
            setCheckedAssets(tmpAssets);
        }
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
                            <BasicDatePicker label="Start Date" handleChange={handleStartSelect} defaultValue={startDate} />
                            <BasicDatePicker label="End Date" handleChange={handleEndSelect} defaultValue={endDate} />
                        </div>
                        <div className="group">
                            <BasicSelect label="Interval" defaultValue={interval} options={defaults.intervals} handleChange={handleIntervalSelect} />
                            <TextField label="Initial Amount" value={initialAmount} onChange={handleAmountSelect} />
                            <TextField label="Episodes" value={numEpisodes} onChange={handleEpisodeSelect} />
                        </div>
                    </div>
                </div>
                <div className="box assets-manager">
                    <div className="title">
                        <h2>Assets Manager</h2>
                        <div className="assets">
                            { defaults.assets.map( (asset, i) => {
                                return (
                                    <FormControlLabel
                                        key={i}
                                        label={asset}
                                        checked={checkedAssets.indexOf(asset) > -1}
                                        control={<Checkbox onChange={() => {checkAsset(asset)}} />}
                                    />
                                )
                            })}
                        </div>
                    </div>
                </div>
            </div>
            <div className="box right-space summary">
                <div className="title">
                    <h2>Summary</h2>
                </div>
                <div className="details">

                </div>
                <Button variant="contained" onClick={ onTrainClick }>Train</Button>
            </div>
        </div>
    )
}
