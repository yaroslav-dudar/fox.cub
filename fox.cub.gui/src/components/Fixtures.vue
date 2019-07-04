<template>
    <div>
        <table class="pure-table pure-table-bordered center">
            <thead>
                <tr>
                    <th>Home Team</th>
                    <th>Away Team</th>
                    <th>Event Date</th>
                    <th>Weather Forecast</th>
                    <th>Detail Stats</th>
                </tr>
            </thead>
            <tr v-for="f in fixtures" :key="f._id">
                <td>{{f.home_name}}</td>
                <td>{{f.away_name}}</td>
                <td>{{f.date.$date}}</td>
                <td>No data</td>
                <td v-if="f.home_id && f.away_id"><button
                    v-on:click="redirectToGame(
                        f.home_id.$oid,
                        f.away_id.$oid,
                        f.tournament_id, f._id)">
                Get Stats</button></td>
                <td v-else>Teams Not available</td>
            </tr>
        </table>
    </div>

</template>

<script>
import router from '@/router'

export default {
    props: ['fixtures'],
    methods: {
        redirectToGame(home_team, away_team,
            tournament, fixture) {

            router.push({
                path: 'game', query: {
                    home_team: home_team,
                    away_team: away_team,
                    tournament: tournament,
                    fixture: fixture
                }
            })
        }
    }
}
</script>
