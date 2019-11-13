<template>
    <highcharts :options="getChartOptions()"></highcharts>
</template>

<script>
import {Chart} from 'highcharts-vue'
import {TournamentMixin} from '@/mixins/TournamentMixin'

export default {
    props: ['games', 'size', 'ppg_table'],
    mixins: [TournamentMixin],
    components: {
        highcharts: Chart
    },
    methods: {
        getChartOptions() {
            var points = this.games.map(
                (v, i) => this.games.slice(0,i+1).slice(-this.size));

            var opponents_strength = points.map(batch => batch.reduce(
                (a, b) => +a + +this.getTeamPPG(this.ppg_table,
                                                b.opponent[0]._id.$oid,
                                                b.tournament), 0) / batch.length)

            return {
                title: { text: "Schedule complexity" },
                xAxis: {
                    type: 'datetime',
                    categories: this.games.map(g => new Date(g.date*1000))
                },
                series: [{
                    name: 'Opoonents point per game',
                    data: opponents_strength
                }]
            }
        },


    }
}
</script>
