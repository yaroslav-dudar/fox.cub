<template>
    <highcharts :options="getChartOptions()" ></highcharts>
</template>

<script>
import {Chart} from 'highcharts-vue';

export default {
    props: ['dataset'],
    components: {
        highcharts: Chart
    },

    methods: {
        getChartOptions() {
            return {
                title: {
                    text: `Dataset distribution`
                },

                xAxis: [{
                    title: { text: 'Data' },
                    alignTicks: false
                }, {
                    title: { text: 'Histogram' },
                    alignTicks: false,
                    opposite: true
                }],

                yAxis: [{
                    title: { text: 'Data' }
                }, {
                    title: { text: 'Histogram' },
                    opposite: true
                }],

                series: [{
                    name: 'Histogram',
                    type: 'histogram',
                    xAxis: 1,
                    yAxis: 1,
                    baseSeries: 's1',
                    zIndex: -1
                }, {
                    name: 'Data',
                    type: 'scatter',
                    data: this.validateDataset() ? this.dataset: [],
                    id: 's1',
                    marker: {
                        radius: 1.5
                    }
                }]
            }
        },

        validateDataset() {
            if (this.dataset.length == 0) return false;
            if (typeof this.dataset[0] != "number") return false;
            return true;
        }
    }
}
</script>
