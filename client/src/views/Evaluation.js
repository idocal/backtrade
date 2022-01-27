import * as React from 'react';


export default function Evaluation(props) {

    return (
      <div className="evaluation">
        {JSON.stringify(props.results.ledger.balances)}
      </div>
    )
}
