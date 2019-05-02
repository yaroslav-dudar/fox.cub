<template>
    <div>
        <form class="pure-form pure-form-aligned">
            <fieldset>
                <div class="pure-control-group">
                    <label for="tournament">Tournament</label>
                    <select v-model="tournament" id="tournament" required>
                        <option
                            v-for="t in $store.state.tournaments" :key="t._id.$oid"
                            v-bind:value='t._id.$oid'> {{t.name}}
                        </option>
                    </select>
                </div>

                <div class="pure-control-group">
                    <label for="tournament_avg_score">Tournament avg. goals</label>
                    <input
                        id="tournament_avg_score" type="number" step="0.01"
                        placeholder="Tournament avg. goals" required v-model="tournament_avg_score">
                </div>

                <div class="pure-control-group">
                    <label for="home_attack">Home Attack</label>
                    <input
                        id="home_attack" type="number" step="0.01"
                        placeholder="Home Team Attack" required v-model="home_attack">
                </div>

                <div class="pure-control-group">
                    <label for="home_defend">Home Defend</label>
                    <input
                        id="home_defend" type="number" step="0.01"
                        placeholder="Home Team Defend" required v-model="home_defend">
                </div>

                <div class="pure-control-group">
                    <label for="away_attack">Away Attack</label>
                    <input
                        id="away_attack" type="number" step="0.01"
                        placeholder="Away Team Attack" required v-model="away_attack">
                </div>

                <div class="pure-control-group">
                    <label for="away_defend">Away Defend</label>
                    <input
                        id="away_defend" type="number" step="0.01"
                        placeholder="Away Team Defend" required v-model="away_defend">
                </div>

                <div class="pure-controls">
                    <button
                        type="submit"
                        class="pure-button pure-button-primary"
                        v-on:click="getStats()">Submit
                    </button>
                </div>
            </fieldset>
        </form>
        <div class="pure-g pure-u-1">
            <h3>Calculated probabilities:</h3>
            <pre v-html="stats"></pre>
        </div>
    </div>
</template>

<script>
import Vue from 'vue'

export default {
    name: 'ManualTest',
    data: function() {
        return {
            tournament: '',
            tournament_avg_score: 0.0,
            home_attack: 0.0,
            home_defend: 0.0,
            away_attack: 0.0,
            away_defend: 0.0,
            stats: {}
        }
    },

    created: function() {
        this.tournament = this.$store.state.tournament;
    },
    methods: {
        getStats() {
            var query = {tournament_id: this.tournament};

            this.$http.post(Vue.config.host + '/api/v1/test/stats', this.getStatsRequest(), {params: query})
                .then(function (response) {
                    this.stats = response.body;
                });
        },

        getStatsRequest() {
            return {
                firstBatch: [{
                    tournament_avg: [{
                        avgScoredHome: parseFloat(this.tournament_avg_score/2),
                        avgScoredAway: parseFloat(this.tournament_avg_score/2)
                    }],
                    home_team: [{
                        scored_xg: [parseFloat(this.home_attack)],
                        conceded_xg: [parseFloat(this.home_defend)]
                    }],
                    away_team: [{
                        scored_xg: [parseFloat(this.away_attack)],
                        conceded_xg: [parseFloat(this.away_defend)]
                    }]
                }]
            }
        }
    }
}
</script>
