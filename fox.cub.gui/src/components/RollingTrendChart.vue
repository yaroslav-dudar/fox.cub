<template>
    <highcharts :options="getChartOptions()"></highcharts>
</template>

<script>
import {Chart} from 'highcharts-vue';

export default {
    props: ['games', 'size', 'metric', 'team_name'],
    components: {
        highcharts: Chart
    },
    methods: {
        getChartOptions() {
            var points = this.games.map((v, i) =>
                this.games.slice(0,i+1).slice(-this.size));

            return {
                title: {
                    text: `${this.size}-game rolling trend for ${this.team_name}`
                },
                xAxis: {
                    type: 'datetime',
                    categories: this.games.map(g => new Date(g.timestamp))
                },
                series: [{
                    name: 'Goals for',
                    data: points.map(batch => batch.reduce(
                        (a, b) => +a + +b.team_data[this.metric], 0) / batch.length)
                }, {
                    name: 'Goals against',
                    data: points.map(batch => batch.reduce(
                        (a, b) => +a + +b.opponent_data[this.metric], 0) / batch.length)
                }]
            }
        }
    }
}
</script>
