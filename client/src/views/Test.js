import * as React from 'react';
import ConfigModal from './ConfigModal';
import defaults from '../defaults';
import Loading from './Loading';
import { useParams } from 'react-router-dom';
import Evaluation from './Evaluation';


export default function Test() {
    const [loading, setLoading] = React.useState(false);
    const [loadingStatus, setLoadingStatus] = React.useState(0);
    const [results, setResults] = React.useState(null);

    const { agentId } = useParams();

    function onTestEnd(res) {
        setLoading(false);
        setResults(res.content);
    }

    async function getTestResults() {
        const URL = '/api/agent/result/' + agentId;
        let response = await fetch(URL);
        response.json().then ( r => {
            console.log(r);
            onTestEnd(r.content);
        });
    }

    async function checkTestStatus() {
        const URL = '/api/agent/status/' + agentId;
        let done = false;
        let interval = setInterval(async () => {
            if (done) {
                clearInterval(interval);
            }
            
            // request training status
            let response = await fetch(URL);
            response.json().then( r => {
                console.dir(r);
                setLoadingStatus(Math.round(Math.min(r.content.test_progress, 1) * 100));
                if (r.content.test_done) {
                    done = true;
                    getTestResults();
                }
            })
            
        }, 100);
    }


    async function testAgent(config) {
        console.log(config);
        config['agent_id'] = agentId;
        const URL = '/api/test';
        return await fetch(URL, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
    }

    async function onTestClick(config) {
        setLoading(true);
        let testRes = await testAgent(config);
        testRes.json().then( res => {
            checkTestStatus();
        })
    }

    return (
        <div className="test">
        { 
            !loading ?
                results === null ?
                    <ConfigModal defaults={defaults} 
                        mode={'test'}
                        onClick={onTestClick}
                        setLoadingStatus={setLoadingStatus} /> :
                <Evaluation results={ results }/>
            :
                <Loading percentage={loadingStatus} /> 
        }
        </div>
    )
}
