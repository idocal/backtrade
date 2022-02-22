import * as React from 'react';
import ConfigModal from './ConfigModal';
import defaults from '../defaults';
import Loading from './Loading';
import { useNavigate } from "react-router-dom";
import './Train.css';


export default function Train(props) {
    const [loading, setLoading] = React.useState(false);
    const [loadingStatus, setLoadingStatus] = React.useState(0);
    const navigate = useNavigate();

    function onTrainEnd() {
        setLoading(false);
        navigate("/");
    }

    async function checkTrainStatus(newAgentId) {
        const URL = 'train/' + newAgentId;
        let done = false;
        let interval = setInterval(async () => {
            if (done) {
                clearInterval(interval);
                onTrainEnd();
            }
            
            // request training status
            let response = await fetch(URL, {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'agent_id': newAgentId})
            });

            response.json().then( r => {
                setLoadingStatus(Math.min(r.train_status, 100));
                if (r.complete) {
                    done = true;
                }
            })
            
        }, 100);
    }

    async function trainAgent(config) {
        const URL = 'train';
        return await fetch(URL, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
    }

    async function onTrainClick(config) {
        setLoading(true);
        const agentRes = await fetch("agent_id");
        agentRes.json().then( async res => {
            // update config with newly created agent
            let newAgentId = res;
            config.agent_id = newAgentId;

            // train new agent
            let trainedAgent = await trainAgent(config);
            trainedAgent.json().then( async () => {
                await checkTrainStatus(newAgentId);
            });
        });
    }

    return (
        <div className="train">
        { 
            !loading ?
                <ConfigModal defaults={defaults} 
                    mode={'train'}
                    onClick={onTrainClick}
                    setLoadingStatus={setLoadingStatus} />
            :
                <Loading percentage={loadingStatus} /> 
        }
        </div>
    )
}
