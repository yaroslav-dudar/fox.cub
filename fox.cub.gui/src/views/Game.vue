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
        <div class="pure-g pure-u-1">
            <h3>Calculated probabilities:</h3>
            <pre v-html="stats"></pre>
        </div>
    </div>  
</template>

<script>
import Vue from 'vue'
import router from '@/router'

import GameOdds from '@/components/GameOdds.vue'
import TeamResults from '@/components/TeamResults.vue'

export default {
    data: function() {
        return {
            home_team: '',
            away_team: '',
            tournament: '',
            home_team_games: [],
            away_team_games: [],
            stats: {},
            odd_list: []
        }
    },
    components: {
        GameOdds,
        TeamResults
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
                });

            this.$http.get(Vue.config.host + '/api/v1/game', {params: away_team_q})
                .then(function (response) {
                    this.away_team_games = response.body.firstBatch;
                });
        },
        redirectToTeam(team_id) {
            router.push({path: '/team', query: { team: team_id }})
        }
    }
}
</script>
