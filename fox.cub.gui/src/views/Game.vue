<template>
    <div>
        <div class="pure-g pure-u-1 center">
        <h1>
        <a v-on:click="redirectToTeam(home_team)">{{game_odds.home_team[0].name}}</a> vs
        <a v-on:click="redirectToTeam(away_team)">{{game_odds.away_team[0].name}}</a>
        </h1>
        </div>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <h3>Home Team Results:</h3>
                <team-results v-bind:games="home_team_games"></team-results>
            </div>
            <div class="pure-u-1-3">
                <h3>Away Team Results:</h3>
                <team-results v-bind:games="away_team_games"></team-results>
            </div>
            <div class="pure-u-1-3">
                <h3>Game Odds History:</h3>
                <game-odds v-bind:odds_history="game_odds.odds"></game-odds>
            </div>
        </div>
        <br>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <team-stats v-bind:stats="home_team_stats"> </team-stats>
                <highcharts :options="getLast6Data('home')"></highcharts>
                <highcharts :options="getRollingTrendData('home')"></highcharts>
            </div>
            <div class="pure-u-1-3">
                <team-stats v-bind:stats="away_team_stats"> </team-stats>
                <highcharts :options="getLast6Data('away')"></highcharts>
                <highcharts :options="getRollingTrendData('away')"></highcharts>
            </div>
        </div>
        <div class="pure-g pure-u-1">
            <h3>Calculated probabilities:</h3>
            <pre v-html="stats"></pre>
        </div>

    </div>
</template>

<script>
import Vue from 'vue'
import router from '@/router'
import {Chart} from 'highcharts-vue'

import GameOdds from '@/components/GameOdds.vue'
import TeamResults from '@/components/TeamResults.vue'
import TeamStats from '@/components/TeamStats.vue'

export default {
    data: function() {
        return {
            home_team: '',
            away_team: '',
            tournament: '',
            home_team_games: [],
            away_team_games: [],
            stats: {},
            odd_list: [],
            home_team_stats: {},
            away_team_stats: {}
        }
    },
    components: {
        GameOdds,
        TeamResults,
        TeamStats,
        highcharts: Chart
    },
    created: function() {
        this.home_team = this.$route.query.home_team;
        this.away_team = this.$route.query.away_team;
        this.tournament = this.$route.query.tournament;
        this.game_odds = this.$store.state.odds[this.$route.query.odd_index];
        this.getGames();
        this.getStats();
    },

    methods: {
        getStats() {
            if (!this.home_team || !this.away_team) {
                alert("Select rivals!");
                return;
            }

            var query = {
                home_team_id: this.home_team,
                away_team_id: this.away_team
            };

            this.$http.get(Vue.config.host + '/api/v1/stats/' + this.tournament, {params: query})
                .then(function (response) {
                    this.stats = response.body;
                });

            this.getGames();
        },
        getGames() {
            var home_team_q = {
                "team_id": this.home_team,
                "tournament_id": this.tournament
            };

            var away_team_q = {
                "team_id": this.away_team,
                "tournament_id": this.tournament
            };

            this.$http.get(Vue.config.host + '/api/v1/game', {params: home_team_q})
                .then(function (response) {
                    this.home_team_games = response.body.firstBatch;
                    this.home_team_stats = this.getTeamPerformance("home");
                });

            this.$http.get(Vue.config.host + '/api/v1/game', {params: away_team_q})
                .then(function (response) {
                    this.away_team_games = response.body.firstBatch;
                    this.away_team_stats = this.getTeamPerformance("away");
                });
        },
        redirectToTeam(team_id) {
            router.push({path: '/team', query: { team: team_id }})
        },

        getTeamPerformance(venue) {
            if (venue == "home") {
                var data = this.home_team_games;
            } else if (venue == "away") {
                data = this.away_team_games;
            }

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

        getLast6Data(venue) {
            var team_name = venue == "home" ? this.game_odds.home_team[0].name: this.game_odds.away_team[0].name;
            var data = venue == "home" ? this.home_team_games: this.away_team_games;
            // print only last 6 games
            data = data.slice(1).slice(-6);

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

        getRollingTrendData(venue) {
            var team_name = venue == "home" ? this.game_odds.home_team[0].name: this.game_odds.away_team[0].name;
            var data = venue == "home" ? this.home_team_games: this.away_team_games;
            var points = data.map((v, i) => data.slice(0,i+1).slice(-10));

            return {
                title: {
                    text: " 10-game rolling trend for " + team_name
                },
                xAxis: {
                    type: 'datetime',
                    categories: data.map(g => new Date(g.date*1000))
                },
                series: [{
                    name: 'Expected goals for',
                    data: points.map(batch => batch.reduce((a, b) => +a + +b.xG_for, 0) / batch.length)
                }, {
                    name: 'Expected goals against',
                    data: points.map(batch => batch.reduce((a, b) => +a + +b.xG_against, 0) / batch.length)
                }]
            }
        }
    }
}
</script>
