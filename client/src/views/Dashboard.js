import Agents from './Agents';
import './Dashboard.css';
import icBalance from '../img/ic-balance.png';
import icAgents from '../img/ic-agents.png';
import icApy from '../img/ic-apy.png';

function Dashboard() {

    let icons = {
        "balance":  icBalance,
        "agents": icAgents,
        "apy": icApy,
    }
    
    function Metric(props) {
        let name = props.name.toLowerCase();
        return (
            <div className="metric">
                <div className="icon-wrapper">
                    <div className="icon" style={{backgroundImage: `url(${icons[name]})`}}/>
                </div>
                <div className="content">
                    <h3>{props.name}</h3>
                    <p className="value">{props.value}</p>
                </div>
            </div>
        )
    }

    return (
        <div className="dashboard">
            <div className="main-space">
                <div className="box active-agent">
                    <div className="metrics">
                        <Metric name="Balance" value="$87,743" />
                        <Metric name="Agents" value="4" />
                        <Metric name="APY" value="+12.3%" />
                    </div>
                </div>
            </div>
            <div className="box right-space">
                <Agents />
            </div>
        </div>
    )
}

export default Dashboard;
