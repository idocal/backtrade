import * as React from 'react';
import _ from 'lodash';
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
const evalCols = [
    { field: 'date', headerName: 'Date', width: 170 },
    { field: 'initial_amount', headerName: 'Initial Amount', width: 130 },
    { field: 'last_balance', headerName: 'Balance', width: 130 },
    { field: 'evaluation_progress', headerName: 'Progress', width: 130 }
];

let evalss = [
    { 'id': 'a', 'date': '2020-01-01', 'initial_amount': 1000, 'last_balance': 15000 },
    { 'id': 'b', 'date': '2020-01-01', 'initial_amount': 1000, 'last_balance': 16000 },
];

function Evaluate() {

    const [evals, setEvals] = React.useState([]);
    const [agents, setAgents] = React.useState([]);
    const [selectedAgent, setSelectedAgent] = React.useState('');
    const [interval, _setInterval] = React.useState('');
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


    const fetchEval = async (evalId) => {
        const URL = '/api/evaluation/get/' + evalId;
        const data = await fetch(URL);
        const json = await data.json();
        let res = json.content;
        console.log(res);
        res['id'] = res.evaluation_id;
        res['last_balance'] = res.last_balance && res['last_balance'].toFixed(2);
        res['date'] = res['date'].replace('T', ' ');
        res['date'] = res['date'].split('.')[0];
        res['evaluation_progress'] = Math.max(0, res.evaluation_progress);
        res['evaluation_progress'] = res['evaluation_progress'].toFixed(2) * 100 + "%";
        if (res["evaluation_done"] === 1) {
            res['evaluation_progress'] = "100%";
        }
        return res;
    }

    const fetchEvals = async (evalIds) => {
        let allEvals = [];
        for ( const evalId of evalIds ) {
            let res = await fetchEval(evalId);
            allEvals = [...allEvals, res];
        }
        return allEvals;
    }

    const updateEvals = () => {
        let localEvals = localStorage.getItem("evals");
        let evalIds = !localEvals ? [] : JSON.parse(localEvals);
        let done = false;

        let interv = setInterval(async () => {
            if (done) {
                clearInterval(interv);
            }
            fetchEvals(evalIds)
                .then( (r) => {
                    setEvals(r);
                    let numDone = _.sumBy(r, e => e.evaluation_done);
                    done = numDone === r.length;
                } )
                .catch(console.error);

        }, 100);
    }

    React.useEffect(() => {
        updateEvals();
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
            updateEvals();
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
                                    _setInterval(selected[0].train_interval);
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
                        <div className="agents-table" style={{height: 400, width: '100%' }}>
                            <DataGrid
                                rows={evals}
                                columns={evalCols}
                                pageSize={10}
                            />
                        </div>
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
