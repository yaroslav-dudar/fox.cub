<template>
    <div>
        <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Home Win</th>
                <th>Draw</th>
                <th>Away Win</th>
                <th>Total</th>
                <th>Total Under</th>
                <th>Total Over</th>
                <th>Scraping Date</th>
            </tr>
        </thead>
        <tr v-for="(o, index) in odds_history" :key="index">
            <td>{{o.moneyline.home}}</td>
            <td>{{o.moneyline.draw}}</td>
            <td>{{o.moneyline.away}}</td>
            <td>{{o.totals[0].points}}</td>
            <td>{{o.totals[0].under}}</td>
            <td>{{o.totals[0].over}}</td>
            <td>{{o.date.$date}}</td>
        </tr>
    </table>
    <highcharts :options="getChartData()"></highcharts>
    </div>

</template>

<script>
import {Chart} from 'highcharts-vue'
export default {
    props: ['odds_history'],
    components: {
        highcharts: Chart
    },
    methods: {
        getChartData() {
            return {
                title: {
                    text: "Game odds"
                },
                xAxis: {
                    type: 'datetime',
                    categories: this.odds_history.map(g => g.date.$date)
                },
                series: [{
                    name: 'Home Win',
                    data: this.odds_history.map(g => [g.moneyline.home])
                }, {
                    name: 'Draw',
                    data: this.odds_history.map(g => g.moneyline.draw)
                }, {
                    name: 'Away Win',
                    data: this.odds_history.map(g => g.moneyline.away)
                }, {
                    name: 'Total',
                    data: this.odds_history.map(g => g.totals[0].points)
                }, {
                    name: 'Total Under',
                    data: this.odds_history.map(g => g.totals[0].under)
                }, {
                    name: 'Total Over',
                    data: this.odds_history.map(g => g.totals[0].over)
                }]
            }
        }
    }
}
</script>
