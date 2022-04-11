import * as React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import './Evaluate.css';


const columns = [
    { field: 'train_start', headerName: 'Start Date', width: 130 },
    { field: 'train_end', headerName: 'End Date', width: 130 },
    { field: 'train_interval', headerName: 'Interval', width: 70 },
    { field: 'symbols', headerName: 'Assets', width: 150 }
];

function Evaluate() {

    let [agents, setAgents] = React.useState([]);

    React.useEffect(() => {
      // declare the async data fetching function
      const fetchData = async () => {
          const URL = '/api/agent/all';
          const data = await fetch(URL);
          const json = await data.json();
          let res = json.content;
          console.log(res);
          setAgents(res);
      }

      // call the function
      fetchData()
        // make sure to catch any error
        .catch(console.error);;
    }, [])

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
                        />
                    </div>
                </div>
            </div>
            <div className="box right-space">
                <div className="title">
                    <h2>Evaluate</h2>
                </div>
                <div className="details">
                </div>
            </div>
        </div>
    )
}

export default Evaluate;
