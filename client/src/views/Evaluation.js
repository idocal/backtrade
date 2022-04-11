import * as React from 'react';
import { useParams, Link} from 'react-router-dom';
import AreaChart from '../components/AreaChart';
import { parse } from 'date-fns';
import { getTime } from 'date-fns';
import './Evaluation.css';


function ledgerToChartData(ledger) {
    let balances = ledger.balances;
    let timestamps = ledger.timestamps
    let unixTimestamps = timestamps.map( (t, i) => {
        t = t.replace('T', ' ');
        let date = parse(t, 'yyyy-MM-dd HH:mm:ss', new Date());
        return getTime(date);
    });
    
    return balances.map((b, i) => {
        return [unixTimestamps[i], b]
    })
}

export default function Evaluation() {
    const { evalId } = useParams();
    const [results, setResults] = React.useState(null);

    React.useEffect(() => {
        const fetchData = async () => {
            const URL = "/api/evaluation/result/" + evalId;
            const data = await fetch(URL);
            const res = await data.json();
            setResults(res.content);
            console.log(res);
        }
        fetchData()
            .catch(console.error)
    }, [])

    return (
      <div className="evaluation modal">
        <div className="main-space">
            <div className="box">
                <div className="title">
                    <Link to="/evaluate"><h2> &larr; </h2></Link>
                    <h2>Agent Evaluation</h2>
                </div>
                <div className="chart">
                    {
                        !!results && (
                            <AreaChart 
                            data={ledgerToChartData(results)}
                            title='Balance over time'
                            metric='Balance'
                            />
                        )
                    }
                </div>
            </div>
        </div>
      </div>
    )

}
