import * as React from 'react';
import AreaChart from './AreaChart';
import { parse } from 'date-fns';
import { getTime } from 'date-fns';


function ledgerToChartData(ledger) {
    let balances = ledger.balances;
    let timestamps = ledger.timestamps
    let unixTimestamps = timestamps.map( (t, i) => {
        let date = parse(t, 'yyyy-MM-dd HH:mm:ss', new Date());
        return getTime(date);
    });
    
    return balances.map((b, i) => {
        return [unixTimestamps[i], b]
    })
}

export default function Evaluation(props) {

    return (
      <div className="evaluation modal">
        <AreaChart 
            data={ledgerToChartData(props.results.ledger)}
            title='Balance over time'
            metric='Balance'
        />
      </div>
    )

}
