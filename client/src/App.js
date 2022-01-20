import BasicSelect from './components/BasicSelect';
import BasicDatePicker from './components/BasicDatePicker';
import Button from '@mui/material/Button';
import './App.css';
import config from './config';

function App() {
  return (
    <div className="App">
      <div className="train-form">
          <BasicSelect label="Coin" options={config.coins} />
          <BasicSelect label="Interval" options={config.intervals} />
          <BasicDatePicker label="Start Date" />
          <BasicDatePicker label="End Date" />
          <Button variant="contained">Train</Button>
      </div>
    </div>
  );
}

export default App;
