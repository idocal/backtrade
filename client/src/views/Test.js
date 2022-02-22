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
            onTestEnd(res);
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
