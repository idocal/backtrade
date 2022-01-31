import './Loading.css';


export default function Loading(props) {
    return (
        <div className="loading">
            <div className="loading-content">
                <div className="double-lines-spinner" />
                <div className="loading-percentage">
                    {props.percentage + '%'}
                </div>
            </div>
        </div>
    )
}
