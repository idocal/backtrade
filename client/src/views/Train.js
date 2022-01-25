import * as React from 'react';
import BasicSelect from '../components/BasicSelect';
import BasicDatePicker from '../components/BasicDatePicker';
import Button from '@mui/material/Button';


export default function Train(props) {

    const [symbol, setSymbol] = React.useState('');
    const [interval, _setInterval] = React.useState('');
    const [startDate, setStartDate] = React.useState('');
    const [endDate, setEndDate] = React.useState('');

    async function trainAgent(config) {
        const URL = 'train';
        let response = await fetch(URL, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        response.json().then(checkTrainStatus());
    }

    async function checkTrainStatus() {
        const URL = 'training_status';
        let done = false;
        let interval = setInterval(async () => {
            if (done) {
                clearInterval(interval);
            }
            
            // request training status
            let response = await fetch(URL);
            response.json().then( r => { console.log(r) } )
            
        }, 100);
    }

    function onTrainClick() {
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
        trainAgent(config);
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
