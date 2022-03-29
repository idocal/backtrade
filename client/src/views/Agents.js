import * as React from 'react';
import { Link } from 'react-router-dom';
import Button from '@mui/material/Button';
import './Agents.css';


function Agents() {

    const [agents, setAgents] = React.useState([]);
    React.useEffect(() => {
      // declare the async data fetching function
      const fetchData = async () => {
        const data = await fetch('/api/agent/all');
        const json = await data.json();
        setAgents(json.content);
          console.log(json.content);
      }

      // call the function
      fetchData()
        // make sure to catch any error
        .catch(console.error);;
    }, [])

    return (
        <div className="agents">
            { agents.map( (agent, i) => {
                return (
                    <div className="agent" key={i}>
                        <Link to={ 'test/' + agent }>
                            { 'Agent #' + (i + 1) }
                        </Link>
                    </div>
                )
            })}
            <Link to="/train">
                <Button variant="contained">
                    Train
                </Button>
            </Link>
        </div>
    )
}

export default Agents
