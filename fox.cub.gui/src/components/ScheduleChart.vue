<template>
    <highcharts :options="getChartOptions()"></highcharts>
</template>

<script>
import {Chart} from 'highcharts-vue'

export default {
    props: ['games', 'size', 'ppg_table'],
    components: {
        highcharts: Chart
    },
    methods: {
        getChartOptions() {
            var points = this.games.map(
                (v, i) => this.games.slice(0,i+1).slice(-this.size));

            var opponents_schedule = points.map(batch => batch.reduce(
                (a, b) => +a + +this.getTeamPPG(b.opponent[0]._id.$oid,
                                                b.tournament), 0) / batch.length)

            return {
                title: { text: "Schedule complexity" },
                xAxis: {
                    type: 'datetime',
                    categories: this.games.map(g => new Date(g.date*1000))
                },
                series: [{
                    name: 'Opoonents point per game',
                    data: opponents_schedule
                }]
            }
        },

        /**
         * Return teams points per game from a specific tournament
         * @return {number}
         */
        getTeamPPG(team_id, tournament_id) {
            var filtered = this.ppg_table[tournament_id]
                .filter(team => team.team_id == team_id);

            if (filtered.length > 0) return filtered[0].ppg;
            return 0;
        }
    }
}
</script>
