import * as React from 'react';
import _ from 'lodash';
import { Link } from 'react-router-dom';
import './Agents.css';


function Agents() {

    const [agents, setAgents] = React.useState([]);
    React.useEffect(() => {
      // declare the async data fetching function
      const fetchData = async () => {
          const URL = '/api/agent/all';

          let done = false;
          let interval = setInterval(async () => {
              if (done) {
                  clearInterval(interval);
              }

              const data = await fetch(URL);
              const json = await data.json();
              let res = json.content;
              setAgents(res);
              let numDone = _.sumBy(res, agent => agent.train_done);
              done = numDone === res.length;

          }, 100);
      }

      // call the function
      fetchData()
        // make sure to catch any error
        .catch(console.error);;
    }, [])

    return (
        <div className="agents">
            <div className="title">
                <h2>Agents</h2>
            </div>
            <div className="list">
                { agents.map( (agent, i) => {
                    let progress = Math.min(agent.train_progress, 1) * 100;
                    let done = progress === 100 ? " done" : "";
                    progress = progress.toString() + "%";
                    return (
                        <div className="agent" key={i}>
                            <Link to={ 'test/' + agent.id }>
                                <p>{ 'Agent #' + (agents.length - i) }</p>
                                <div className={ "progress-bar" + done }>
                                    <div className="progress" style={{"width": progress}}/>
                                </div>
                            </Link>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

export default Agents
