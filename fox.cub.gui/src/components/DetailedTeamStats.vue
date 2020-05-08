<template>
    <div >
        <table class="pure-table" style="width: 50%">
            <thead>
                <tr>
                    <th>Actual goals scored</th>
                    <th>Actual goals conceded
                        <select v-model="selected_type" style="float: right;">
                            <option
                                v-for="(type,i) in stats_types"
                                :key="i" v-bind:value="type">
                                {{ type }}
                            </option>
                        </select>
                    </th>
                </tr>
            </thead>
            <tr>
                <td v-if="stats.actual">{{stats.actual.scored.toFixed(3)}}</td>
                <td v-else> No data </td>
                <td v-if="stats.actual">{{stats.actual.conceded.toFixed(3)}}</td>
                <td v-else> No data </td>
            </tr>
        </table>
        <br>
        <table class="pure-table" style="width: 50%">
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
        <br>
        <table class="pure-table" style="width: 50%">
            <thead>
                <tr>
                    <th>Home Teams score per game</th>
                    <th>Away Teams score per game</th>
                </tr>
            </thead>
            <tr>
                <td v-if="home_adv">
                    {{home_adv.avgGoalsHome.toFixed(3)}}
                    ({{home_adv.avgxGHome.toFixed(3)}} xG)
                </td>
                <td v-else> No data </td>
                <td v-if="home_adv">
                    {{home_adv.avgGoalsAway.toFixed(3)}}
                    ({{home_adv.avgxGAway.toFixed(3)}} xG)
                </td>
                <td v-else> No data </td>
            </tr>
        </table>
        <br>
        <table class="pure-table" style="width: 50%">
            <thead>
                <tr>
                    <th>Opponnet avg points</th>
                    <th>Opponnet avg scoring</th>
                    <th>Opponnet avg conceding</th>
                </tr>
            </thead>
            <tr>
                <td>{{getOpponentsStrength()}} ({{getTournamentStats()}})</td>
                <td>{{getOpponentsStrength("spg")}} ({{getTournamentStats("spg")}})</td>
                <td>{{getOpponentsStrength("cpg")}} ({{getTournamentStats("cpg")}})</td>
            </tr>
        </table>

    </div>
</template>

<script>
import {TournamentMixin} from '@/mixins/TournamentMixin'
import { mapGetters } from "vuex";

export default {
    props: ['games', 'home_adv'],
    mixins: [TournamentMixin],

    computed: {
        ...mapGetters([
            "ppg_table"
        ])
    },

    data: function() {
        return {
            stats: {},
            opponents_str: 0,
            stats_types: ['all', 'home', 'away'],
            selected_type: 'all'
        }
    },
    created: function() {
        this.stats = this.getTeamPerformance();
    },
    watch: {
        games: {
            handler: function() {
                this.calc_stats(),
                this.opponents_str = this.getOpponentsStrength();
            },
            deep: true
        },
        selected_type: {
            handler: function() { this.calc_stats() },
            deep: true
        }
    },
    methods: {
        calc_stats() {
            this.stats = this.getTeamPerformance(this.selected_type);
        },
        getTeamPerformance(venue) {
            let data = this.games.filter(game => {
                if (!game.selected) return false;

                if (venue == "all")
                    return true
                else if (venue == "home")
                    return game.venue == "home";
                else if (venue == "away")
                    return game.venue == "away";
            });

            var xg = {
                "scored": data.reduce((a, b) => +a + +b.xG_for, 0) / data.length,
                "conceded": data.reduce((a, b) => +a + +b.xG_against, 0) / data.length
            }
            var actual = {
                "scored": data.reduce((a, b) => +a + +b.goals_for, 0) / data.length,
                "conceded": data.reduce((a, b) => +a + +b.goals_against, 0) / data.length
            }

            return {xg: xg, actual: actual}
        },

        getOpponentsStrength(metric = "ppg") {
            let selected_games = this.games.filter(g => g.selected);
            return (selected_games
                .map(g => this.getTeamPPG(this.ppg_table,
                                          g.opponent_id,
                                          g.tournament,
                                          metric))
                .reduce((a, c) => {return a + c }) /
                    selected_games.length).toFixed(3);
        },

        getTournamentStats(metric = "ppg") {
            let tournament = this.games.filter(g => g.selected)[0].tournament;
            return (this.ppg_table[tournament]
                .map(t => t[metric])
                .reduce((a, c) => {return a + c }) /
                    this.ppg_table[tournament].length).toFixed(3);
        }
    }
}
</script>
