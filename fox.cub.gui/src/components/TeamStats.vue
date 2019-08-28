<template>
    <div >
        <table class="pure-table" style="width: 80%">
            <thead>
                <tr>
                    <th>Actual goals scored</th>
                    <th>Actual goals conceded</th>
                </tr>
            </thead>
            <tr>
                <td v-if="stats.actual">{{stats.actual.scored.toFixed(3)}}</td>
                <td v-else> No data </td>
                <td v-if="stats.actual">{{stats.actual.conceded.toFixed(3)}}</td>
                <td v-else> No data </td>
            </tr>
        </table>
        <table class="pure-table" style="width: 80%">
            <thead>
                <tr>
                    <th>Expected goals scored</th>
                    <th>Expected goals conceded</th>
                </tr>
            </thead>
            <tr>
                <td v-if="stats.xg">{{stats.xg.scored.toFixed(3)}}</td>
                <td v-else> No data </td>
                <td v-if="stats.xg">{{stats.xg.conceded.toFixed(3)}}</td>
                <td v-else> No data </td>
            </tr>
        </table>
    </div>
</template>

<script>
export default {
    props: ['games'],
    data: function() {
        return {
            stats: {}
        }
    },
    created: function() {
        this.stats = this.getTeamPerformance();
    },
    watch: {
        games: {
            handler: function() {
                this.stats = this.getTeamPerformance();
            },
            deep: true
        }
    },
    methods: {
        getTeamPerformance() {
            let data = this.games.filter(game => game.selected == true);

            var xg = {
                "scored": data.reduce((a, b) => +a + +b.xG_for, 0) / data.length,
                "conceded": data.reduce((a, b) => +a + +b.xG_against, 0) / data.length
            }
            var actual = {
                "scored": data.reduce((a, b) => +a + +b.goals_for, 0) / data.length,
                "conceded": data.reduce((a, b) => +a + +b.goals_against, 0) / data.length
            }

            return {xg: xg, actual: actual}
        }
    }
}
</script>
