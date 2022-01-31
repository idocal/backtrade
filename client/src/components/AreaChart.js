import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';


export default function AreaChart(props) {

    let options = {

        rangeSelector: {
            selected: 1
        },

        title: {
            text: props.title
        },

        series: [{
            name: props.metric,
            data: props.data,
            type: 'area',
            threshold: null,
            tooltip: {
                valueDecimals: 2
            },
            fillColor: {
                linearGradient: {
                    x1: 0,
                    y1: 0,
                    x2: 0,
                    y2: 1
                },
                stops: [
                    [0, Highcharts.getOptions().colors[0]],
                    [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                ]
            }
        }]
    }

    return (
        <div>
            <HighchartsReact
                constructorType="stockChart"
                highcharts={Highcharts}
                options={options}
            />
        </div>
    )
}
