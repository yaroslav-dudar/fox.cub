<template>
    <highcharts :options="getChartOptions()"></highcharts>
</template>

<script>
import {Chart} from 'highcharts-vue'

export default {
    props: ['games', 'team_name'],
    components: {
        highcharts: Chart
    },
    methods: {
        getChartOptions() {
            // print only last 6 games
            let last_games = this.games.length > 0 ?
                this.games.slice(-6) : this.games;

            return {
                chart: { type: 'column' },
                title: { text: this.team_name + " last 6 games" },
                series: [{
                    name: 'Expected goals for',
                    data: last_games.map(g => g.xG_for)
                }, {
                    name: 'Expected goals against',
                    data: last_games.map(g => g.xG_against)
                }, {
                    name: 'Expected goals diff',
                    data: last_games.map(g => g.xG_for - g.xG_against)
                }]
            };
        }
    }
}
</script>
