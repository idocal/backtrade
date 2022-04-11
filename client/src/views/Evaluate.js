import * as React from 'react';
import TextField from '@mui/material/TextField';
import BasicDatePicker from '../components/BasicDatePicker';
import Button from '@mui/material/Button';
import { isValid, format } from 'date-fns';
import { DataGrid } from '@mui/x-data-grid';
import './Evaluate.css';


const PROVIDER = 'binance';
const columns = [
    { field: 'train_start', headerName: 'Start Date', width: 130 },
    { field: 'train_end', headerName: 'End Date', width: 130 },
    { field: 'train_interval', headerName: 'Interval', width: 70 },
    { field: 'symbols', headerName: 'Assets', width: 150 }
];

function Evaluate() {

    const [evals, setEvals] = React.useState([]);
    const [agents, setAgents] = React.useState([]);
    const [selectedAgent, setSelectedAgent] = React.useState('');
    const [interval, setInterval] = React.useState('');
    const [startDate, setStartDate] = React.useState(new Date('2020-01-01T00:00:00'));
    const [endDate, setEndDate] = React.useState(new Date('2020-02-01T00:00:00'));
    const [initialAmount, setInitialAmount] = React.useState(10000);

    React.useEffect(() => {
      // declare the async data fetching function
      const fetchData = async () => {
          const URL = '/api/agent/all';
          const data = await fetch(URL);
          const json = await data.json();
          let res = json.content;
          setAgents(res);
      }

      // call the function
      fetchData()
        // make sure to catch any error
        .catch(console.error);;
    }, [])

    function handleStartSelect(date) {
        setStartDate(date);
    }

    function handleEndSelect(date) {
        setEndDate(date);
    }

    function handleAmountSelect(e) {
        setInitialAmount(e.target.value);
    }

    async function onTestClick() {
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
            "agent_id": selectedAgent,
            "start_date": formattedStartDate,
            "end_date": formattedEndDate,
            "initial_amount": initialAmount,
            "interval": interval,
        }

        const URL = '/api/test';
        const res = await fetch(URL, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        res.json().then( r => {
            let evalId = r.content.evaluation_id;
            let allEvals = JSON.parse(localStorage.getItem("evals"));
            allEvals = !allEvals ? [] : allEvals;  // if no evals exist
            let newEvals = [...allEvals, evalId];
            localStorage.setItem("evals", JSON.stringify(newEvals));
            setEvals(newEvals);
        })
    }

    return (
        <div className="evaluate">
            <div className="main-space">
                <div className="box">
                    <div className="title">
                        <h2>Agents</h2>
                    </div>
                    <div className="agents-table" style={{height: 400, width: '100%' }}>
                        <DataGrid
                            rows={agents}
                            columns={columns}
                            pageSize={10}
                            onSelectionModelChange={ (ids) => {
                                if (ids.length) {
                                    let _id = ids[0];
                                    setSelectedAgent(_id);
                                    let selected = agents.filter(agent => {
                                        return agent.id === _id;
                                    });
                                    setInterval(selected[0].train_interval);
                                } else {
                                    setSelectedAgent('');
                                }
                            }}
                        />
                    </div>
                </div>
                <div className="evals">
                    <div className="box">
                        <div className="title">
                            <h2>Evaluations</h2>
                        </div>
                        { localStorage.getItem("evals") && JSON.parse(localStorage.getItem("evals")).toString() }
                    </div>
                </div>
            </div>
            <div className="box right-space summary">
                <div className="title">
                    <h2>Evaluate</h2>
                </div>
                <div className="details">
                    <div className="control">
                        <BasicDatePicker label="Start Date" handleChange={handleStartSelect} defaultValue={startDate} />
                    </div>
                    <div className="control">
                        <BasicDatePicker label="End Date" handleChange={handleEndSelect} defaultValue={endDate} />
                    </div>
                    <div className="control">
                        <TextField label="Initial Amount" value={initialAmount} onChange={handleAmountSelect} />
                    </div>
                </div>
                <Button variant="contained" disabled={!selectedAgent.length} onClick={ onTestClick }>Evaluate</Button>
            </div>
        </div>
    )
}

export default Evaluate;
