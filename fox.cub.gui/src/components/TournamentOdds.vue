<template>
    <table class="pure-table pure-table-bordered center">
        <thead>
            <tr>
                <th>Home Team</th>
                <th>Away Team</th>
                <th>Home Win</th>
                <th>Draw</th>
                <th>Away Win</th>
                <th>Total</th>
                <th>Total Under</th>
                <th>Total Over</th>
                <th>Event Date</th>
                <th>Detail Stats</th>
            </tr>
        </thead>
        <tr v-for="(o,i) in odds" :key="o._id.$oid">
            <td>{{o.home_team[0].name}}</td>
            <td>{{o.away_team[0].name}}</td>
            <td>{{o.odds[o.odds.length-1].home_win}}</td>
            <td>{{o.odds[o.odds.length-1].draw}}</td>
            <td>{{o.odds[o.odds.length-1].away_win}}</td>
            <td>{{o.odds[o.odds.length-1].total}}</td>
            <td>{{o.odds[o.odds.length-1].total_under}}</td>
            <td>{{o.odds[o.odds.length-1].total_over}}</td>
            <td>{{o.event_date.$date}}</td>
            <td><button
                v-on:click="redirectToGame(
                    o.home_team[0]._id['$oid'],
                    o.away_team[0]._id['$oid'],
                    o.tournament, i)">
            Get Stats</button></td>
        </tr>
    </table>
</template>

<script>
import router from '@/router'

export default {
    props: ['odds'],
    methods: {
        redirectToGame(home_team, away_team,
            tournament, indx) {

            router.push({
                path: 'game', query: {
                    home_team: home_team,
                    away_team: away_team,
                    tournament: tournament,
                    odd_index: indx
                }
            })
        }
    }
}
</script>
