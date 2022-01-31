import * as React from 'react';
import BasicSelect from '../components/BasicSelect';
import BasicDatePicker from '../components/BasicDatePicker';
import Button from '@mui/material/Button';


export default function Train(props) {

    const [symbol, setSymbol] = React.useState('');
    const [interval, _setInterval] = React.useState('');
    const [startDate, setStartDate] = React.useState('');
    const [endDate, setEndDate] = React.useState('');

    async function createAgent() {
        const URL = 'agent_id';
        console.log('creating agent');
        return await fetch(URL);
    }

    async function trainAgent(config) {
        console.log('training agent');
        console.log(config);
        const URL = 'train';
        return await fetch(URL, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
    }

    async function checkTrainStatus(agentId) {
        const URL = 'training_status';
        let done = false;
        let interval = setInterval(async () => {
            if (done) {
                clearInterval(interval);
            }
            
            // request training status
            let response = await fetch(URL, {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'agent_id': agentId})
            });
            response.json().then( r => {
                console.log(r) 
                props.setLoadingStatus(r.training_status);
                if (r.complete) {
                    console.log('complete');
                    done = true;
                }
            })
            
        }, 100);
    }

    async function onTrainClick() {
        let config = {
            "symbol": symbol,
            "interval": interval,
            "start": startDate,
            "end": endDate,
            "initial_amount": 10000,
            "commission": 0.00075,
            "num_steps": 10000
        }
        props.onTrainClick();
        let newAgent = await createAgent();
        newAgent.json().then( async agentRes => {
            let agentId = agentRes.agent_id;
            config['agent_id'] = agentId;
            console.log(config);
            let trainedAgent = await trainAgent(config);
            trainedAgent.json().then( async () => {
                await checkTrainStatus(agentId);
            });
        });
    }

    function handleCoinSelect(e) {
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

    return (
      <div className="train-form">
          <BasicSelect label="Coin" options={props.config.coins} handleChange={handleCoinSelect} />
          <BasicSelect label="Interval" options={props.config.intervals} handleChange={handleIntervalSelect} />
          <BasicDatePicker label="Start Date" handleChange={handleStartSelect} />
          <BasicDatePicker label="End Date" handleChange={handleEndSelect} />
          <Button variant="contained" onClick={onTrainClick}>Train</Button>
      </div>
    )
}
