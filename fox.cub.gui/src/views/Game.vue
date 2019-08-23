<template>
    <div>
        <div class="pure-g pure-u-1 center">
        <h1>
        <a v-on:click="redirectToTeam(home_team)">{{fixture.home_name}}</a> vs
        <a v-on:click="redirectToTeam(away_team)">{{fixture.away_name}}</a>
        </h1>
        </div>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <h3>Home Team Results:</h3>
                <team-results v-bind:games="home_games"></team-results>
            </div>
            <div class="pure-u-1-3">
                <h3>Away Team Results:</h3>
                <team-results v-bind:games="away_games"></team-results>
            </div>
            <div class="pure-u-1-3">
                <h3>Game Odds History:</h3>
                <game-odds v-bind:odds_history="odds"></game-odds>
            </div>
        </div>
        <br>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <team-stats v-bind:stats="home_team_stats"> </team-stats>
                <highcharts :options="getLast6Data('home')"></highcharts>
            </div>
            <div class="pure-u-1-3">
                <team-stats v-bind:stats="away_team_stats"> </team-stats>
                <highcharts :options="getLast6Data('away')"></highcharts>
            </div>
        </div>
        <br>
        <div class="pure-g">
            <div class="pure-u-1-3">
                Select trend size:
                <select name="trendSize" v-model="rolling_trend_size" class="form-control">
                    <option value="6">6 games trend</option>
                    <option value="10">10 games trend</option>
                </select>
                <highcharts :options="getRollingTrendData('home', rolling_trend_size, rolling_trend_type)" ref="home-trend"></highcharts>
            </div>
            <div class="pure-u-1-3">
                Select type of goals:
                <select name="trendType" v-model="rolling_trend_type" class="form-control">
                    <option value="xG">Expected goals Ingogol</option>
                    <option value="goals">Actual goals</option>
                </select>
                <highcharts :options="getRollingTrendData('away', rolling_trend_size, rolling_trend_type)" ref="away-trend"></highcharts>
            </div>
        </div>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <highcharts :options="getShcheduleComplexity('home', rolling_trend_size)"></highcharts>
            </div>
            <div class="pure-u-1-3">
                <highcharts :options="getShcheduleComplexity('away', rolling_trend_size)"></highcharts>
            </div>
        </div>
        <div class="pure-g pure-u-1">
            <h3>Calculated probabilities:</h3>
            <pre v-html="stats"></pre>
        </div>
    </div>
</template>

<script>
import { mapGetters } from "vuex";
import router from '@/router'
import {Chart} from 'highcharts-vue'

import GameOdds from '@/components/GameOdds.vue'
import TeamResults from '@/components/TeamResults.vue'
import TeamStats from '@/components/TeamStats.vue'
import {
    FETCH_GAMES,
    FETCH_ODDS,
    FETCH_STATS
} from '@/store/actions.type'


export default {
    computed: {
        ...mapGetters([
            "home_games", "away_games", "odds",
            "ppg_table", "fixtures", "stats"
        ])
    },

    data: function() {
        return {
            home_team: '',
            away_team: '',
            tournament: '',
            fixture: {},
            home_team_stats: {},
            away_team_stats: {},
            rolling_trend_size: 6,
            rolling_trend_type: 'xG' // allowed [xG, goals]
        }
    },
    components: {
        GameOdds,
        TeamResults,
        TeamStats,
        highcharts: Chart
    },
    created: function() {
        let fixture_id = this.$route.query.fixture;

        this.fixture = this.fixtures.find(f => f._id.$oid == fixture_id);
        this.home_team = this.fixture.home_id.$oid;
        this.away_team = this.fixture.away_id.$oid;
        this.tournament = this.fixture.tournament_id;

        this.$store.dispatch(FETCH_GAMES,
            {
                team_id: this.home_team,
                tournament_id: null,
                venue: 'home'
            });

        this.$store.dispatch(FETCH_GAMES,
            {
                team_id: this.away_team,
                tournament_id: null,
                venue: 'away'
            });

        this.$store.dispatch(FETCH_ODDS, this.fixture.external_ids);
        this.$store.dispatch(FETCH_STATS, {
            home_team_id: this.home_team,
            away_team_id: this.away_team,
            tournament_id: this.tournament
        });
    },

    watch: {
        home_games() {
            // is triggered whenever the store state changes
            this.home_team_stats = this.getTeamPerformance("home");
        },
        away_games() {
            // is triggered whenever the store state changes
            this.away_team_stats = this.getTeamPerformance("away");
        }
    },
    methods: {
        redirectToTeam(team_id) {
            router.push({path: '/team', query: { team: team_id }})
        },

        getTeamPerformance(venue) {
            if (venue == "home") {
                var data = this.home_games;
            } else if (venue == "away") {
                data = this.away_games;
            }
            data = data.filter(game => game.tournament == this.tournament);

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

        /**
         * Calculate last 6 games data and encapsulate
         * it to highcarts API object
         */
        getLast6Data(venue) {
            var team_name = venue == "home" ?
                this.fixture.home_name :
                this.fixture.away_name;

            var data = venue == "home" ?
                this.home_games :
                this.away_games;

            // print only last 6 games
            data = data.slice(-6);

            return {
                chart: {
                    type: 'column'
                },
                title: {
                    text: team_name + " last 6 games"
                },
                series: [{
                    name: 'Expected goals for',
                    data: data.map(g => g.xG_for)
                }, {
                    name: 'Expected goals against',
                    data: data.map(g => g.xG_against)
                }, {
                    name: 'Expected goals diff',
                    data: data.map(g => g.xG_for - g.xG_against)
                }]
            }
        },

        /**
         * Calculate rolling trend data array
         * and encapsulate it to highcarts API object
         */
        getRollingTrendData(venue, games_amount = 6, goals_type = "xG") {
            var team_name = venue == "home" ?
                this.fixture.home_name :
                this.fixture.away_name;

            var data = venue == "home" ?
                this.home_games :
                this.away_games;

            var points = data.map((v, i) => data.slice(0,i+1).slice(-games_amount));

            return {
                title: {
                    text: " 10-game rolling trend for " + team_name
                },
                xAxis: {
                    type: 'datetime',
                    categories: data.map(g => new Date(g.date*1000))
                },
                series: [{
                    name: 'Goals for',
                    data: points.map(batch => batch.reduce(
                        (a, b) => +a + +b[goals_type + "_for"], 0) / batch.length)
                }, {
                    name: 'Goals against',
                    data: points.map(batch => batch.reduce(
                        (a, b) => +a + +b[goals_type + "_against"], 0) / batch.length)
                }]
            }
        },

        /**
         * Calculate sequence of opponents PPG
         */
        getShcheduleComplexity(venue, games_amount = 6) {
            var data = venue == "home" ? this.home_games : this.away_games;
            var points = data.map(
                (v, i) => data.slice(0,i+1).slice(-games_amount));

            var opponents_schedule = points.map(batch => batch.reduce(
                (a, b) => +a + +this.getTeamPPG(b.opponent[0]._id.$oid,
                                                b.tournament), 0) / batch.length)

            return {
                title: {
                    text: "Schedule complexity"
                },
                xAxis: {
                    type: 'datetime',
                    categories: data.map(g => new Date(g.date*1000))
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
