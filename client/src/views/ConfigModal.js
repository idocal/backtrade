import * as React from 'react';
import BasicSelect from '../components/BasicSelect';
import BasicDatePicker from '../components/BasicDatePicker';
import Button from '@mui/material/Button';


export default function ConfigModal(props) {

    const [symbol, setSymbol] = React.useState('BTC');
    const [interval, _setInterval] = React.useState('');
    const [startDate, setStartDate] = React.useState('');
    const [endDate, setEndDate] = React.useState('');


    async function onButtonClick() {
        let config = {
            "symbol": symbol,
            "interval": interval,
            "start": startDate,
            "end": endDate,
            "initial_amount": 10000,
            "commission": 0.00075,
            "num_steps": 10000
        }
        await props.onClick(config);
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
      <div className="modal">
        { props.mode !== 'test' &&
            <BasicSelect label="Coin" options={props.defaults.coins} handleChange={handleCoinSelect} />
        }
        <BasicSelect label="Interval" options={props.defaults.intervals} handleChange={handleIntervalSelect} />
        <BasicDatePicker label="Start Date" handleChange={handleStartSelect} />
        <BasicDatePicker label="End Date" handleChange={handleEndSelect} />
        <Button variant="contained" onClick={ onButtonClick }>
            { props.mode }
        </Button>
      </div>
    )
}
