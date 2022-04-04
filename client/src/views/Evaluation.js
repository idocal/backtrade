import * as React from 'react';
import AreaChart from '../components/AreaChart';
import { parse } from 'date-fns';
import { getTime } from 'date-fns';


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

export default function Evaluation(props) {
    console.log('evaluation');
    console.log(props.results);

    return (
      <div className="evaluation modal">
        <AreaChart 
            data={ledgerToChartData(props.results)}
            title='Balance over time'
            metric='Balance'
        />
      </div>
    )

}
