import * as React from 'react';
import BasicSelect from './components/BasicSelect';
import BasicDatePicker from './components/BasicDatePicker';
import Button from '@mui/material/Button';
import './App.css';
import config from './config';


async function trainAgent(config) {
    const URL = '/train';
    const response = await fetch(URL, {
          method: 'POST',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(config)
        });
    return response
}

function App() {
    const [symbol, setSymbol] = React.useState('');
    const [interval, _setInterval] = React.useState('');
    const [startDate, setStartDate] = React.useState('');
    const [endDate, setEndDate] = React.useState('');

    function onTrainClick() {
        let config = {
            "coin": symbol,
            "interval": interval,
            "start": startDate,
            "end": endDate,
            "initial_amount": 10000,
            "commission": 0.00075,
            "num_steps": 10000
        }
        console.log(config);
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
    <div className="App">
      <div className="train-form">
          <BasicSelect label="Coin" options={config.coins} handleChange={handleCoinSelect} />
          <BasicSelect label="Interval" options={config.intervals} handleChange={handleIntervalSelect} />
          <BasicDatePicker label="Start Date" handleChange={handleStartSelect} />
          <BasicDatePicker label="End Date" handleChange={handleEndSelect} />
          <Button variant="contained" onClick={onTrainClick}>Train</Button>
      </div>
    </div>
  );
}

export default App;
