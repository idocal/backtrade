import * as React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';
import icDashboard from '../img/ic-dasboard.png';
import icTrain from '../img/ic-train.png';
import icEvaluate from '../img/ic-evaluate.png';


const icons = {
    "dashboard": icDashboard,
    "train": icTrain,
    "evaluate": icEvaluate
}


function Navbar() {
    const location = useLocation();
    let [active, setActive] = React.useState(location.pathname);

    React.useEffect(() => {
        setActive(location.pathname);
    }, [location])

    function onNavBarItemClick(name) {
        setActive(name);
    }

    function NavbarItem(props) {
        let name = props.name.toLowerCase();
        let activeClass = props.link === active ? " active" : "";
        return (
            <Link to={props.link}>
                <div className={ "navbar-item" + activeClass } onClick={ () => {onNavBarItemClick(props.link)} }>
                    <div className="navbar-icon" style={{ backgroundImage: `url(${icons[name]})`  }} />
                    {props.name}
                </div>
            </Link>
        )
    }

    return (
        <div className="nav-space">
            <div className="navbar">
                <NavbarItem name="Dashboard" link="/" active />
                <NavbarItem name="Train" link="/train" />
                <NavbarItem name="Evaluate" link="/evaluate" />
            </div>
        </div>
    )
}

export default Navbar;
