import './Header.css';

function Header() {
    return (
        <div className="header">
            <div className="nav-space">
                <a href="/"><div className="logo" /></a>
            </div>
            <div className="main-space">
                <h2>Welcome back, Ido</h2>
            </div>
            <div className="right-space">
                <div className="account-icon" />
            </div>
        </div>
    )
}

export default Header
