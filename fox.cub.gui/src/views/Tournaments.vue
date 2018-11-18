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
        <tournament-odds v-bind:odds="$store.state.odds"></tournament-odds>
    </div>
</template>

<script>
import Vue from 'vue'
import TournamentOdds from '@/components/TournamentOdds.vue'

export default {
    name: 'Tournaments',
    data: function() {
        return {
            tournaments: [],
            tournament: '',
            odds: [],
            teams: []
        }
    },
    components: {
        TournamentOdds
    },

    created: function() {
        this.tournament = this.$store.state.tournament;
    },
    methods: {
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
        }
    }
}
</script>
