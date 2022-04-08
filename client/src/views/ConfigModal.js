import * as React from 'react';
import BasicSelect from '../components/BasicSelect';
import BasicDatePicker from '../components/BasicDatePicker';
import Button from '@mui/material/Button';
import MultipleSelectChip from '../components/MultipleSelectChip';
import './ConfigModal.css';

const PROVIDER = 'binance';

export default function ConfigModal(props) {

    const [symbol, setSymbol] = React.useState([]);
    const [interval, _setInterval] = React.useState('');
    const [startDate, setStartDate] = React.useState('');
    const [endDate, setEndDate] = React.useState('');


    async function onButtonClick() {
        let config = {
            "provider": PROVIDER,
            "symbols": symbol,
            "interval": interval,
            "start_date": startDate,
            "end_date": endDate,
            "initial_amount": 10000,
            "commission": 0.00075
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
            <MultipleSelectChip vals={props.defaults.coins} label="Coin" handleSelect={handleCoinSelect}/>
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
