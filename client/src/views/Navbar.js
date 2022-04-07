import * as React from 'react';
import { Link } from 'react-router-dom';
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
    let [active, setActive] = React.useState('dashboard')

    function onNavBarItemClick(name) {
        setActive(name);
    }

    function NavbarItem(props) {
        let name = props.name.toLowerCase();
        let activeClass = name === active ? " active" : "";
        return (
            <Link to={props.link}>
                <div className={ "navbar-item" + activeClass } onClick={ () => {onNavBarItemClick(name)} }>
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
