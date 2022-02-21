import * as React from 'react';
import ConfigModal from './ConfigModal';
import defaults from '../defaults';
import Loading from './Loading';
import { useParams } from 'react-router-dom';


export default function Test(props) {
    const [loading, setLoading] = React.useState(false);
    const [loadingStatus, setLoadingStatus] = React.useState(0);
    const [results, setResults] = React.useState(null);

    const { agentId } = useParams();

    function onTestEnd(res) {
        setLoading(false);
        setResults(res);
    }

    async function testAgent(config) {
        const URL = 'test';
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
                <ConfigModal defaults={defaults} 
                    mode={'test'}
                    onClick={onTestClick}
                    setLoadingStatus={setLoadingStatus} />
            :
                <Loading percentage={loadingStatus} /> 
        }
        </div>
    )
}
