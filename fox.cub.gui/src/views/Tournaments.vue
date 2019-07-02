<template>
    <div>
        <h3>Select Tournament</h3>
        <select v-model="tournament" @change="onChange()">
            <option
                v-for="t in $store.state.tournaments" :key="t._id.$oid"
                v-bind:value='t._id.$oid'> {{t.name}}
            </option>
        </select>
        <h3>Tournament Odds:</h3>
        <fixtures
            v-bind:odds="$store.state.odds"
            v-bind:fixtures="$store.state.fixtures">
        </fixtures>
    </div>
</template>

<script>
import Vue from 'vue'
import Fixtures from '@/components/Fixtures.vue'

export default {
    name: 'Tournaments',
    data: function() {
        return {
            tournaments: [],
            ppg_table: [],
            tournament: '',
            odds: [],
            fixtures: [],
            teams: []
        }
    },
    components: {
        Fixtures
    },

    created: function() {
        this.tournament = this.$store.state.tournament;
        this.ppg_table = this.$store.state.ppg_table;
    },
    methods: {
        /**
         * @desc pre-load tournament data
        */
        onChange() {
            this.$store.commit('setCurrentTournament', this.tournament)

            this.$http.get(Vue.config.host + '/api/v1/team/' + this.tournament)
                .then(function (response) {
                    this.teams = response.body.firstBatch;
                });

            this.$http.get(Vue.config.host + '/api/v1/odds/' + this.tournament)
                .then(function (response) {
                    this.odds = response.body.firstBatch;
                    this.$store.commit('setOdds', this.odds)
                });

            this.$http.get(Vue.config.host + '/api/v1/tournament/' + this.tournament)
                .then(function (response) {
                    this.ppg_table = response.body.table;
                    this.$store.commit('setPPGTable', this.ppg_table)
                });

            this.$http.get(Vue.config.host + '/api/v1/fixtures?tournament_id=' + this.tournament)
                .then(function (response) {
                    this.fixtures = response.body.firstBatch;
                    this.$store.commit('setFixtures', this.fixtures)
                });
        }
    }
}
</script>
