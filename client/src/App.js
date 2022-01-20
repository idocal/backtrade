import BasicSelect from './components/BasicSelect';
import './App.css';
import config from './config';

function App() {
  return (
    <div className="App">
      <div className="train-form">
          <BasicSelect label="Coin" options={config.coins} />
          <BasicSelect label="Interval" options={config.intervals} />
      </div>
    </div>
  );
}

export default App;
