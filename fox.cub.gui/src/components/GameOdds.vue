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
            <td>{{o.home_win}}</td>
            <td>{{o.draw}}</td>
            <td>{{o.away_win}}</td>
            <td>{{o.total}}</td>
            <td>{{o.total_under}}</td>
            <td>{{o.total_over}}</td>
            <td>{{o.scraping_date.$date}}</td>
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
                    categories: this.odds_history.map(g => g.scraping_date.$date)
                },
                series: [{
                    name: 'Home Win',
                    data: this.odds_history.map(g => [g.home_win])
                }, {
                    name: 'Draw',
                    data: this.odds_history.map(g => g.draw)
                }, {
                    name: 'Away Win',
                    data: this.odds_history.map(g => g.away_win)
                }, {
                    name: 'Total',
                    data: this.odds_history.map(g => g.total)
                }, {
                    name: 'Total Under',
                    data: this.odds_history.map(g => g.total_under)
                }, {
                    name: 'Total Over',
                    data: this.odds_history.map(g => g.total_over)
                }]
            }
        }
    }
}
</script>
