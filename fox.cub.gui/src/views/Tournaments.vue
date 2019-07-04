<template>
    <div>
        <h3>Select Tournament</h3>
        <select v-model="tournament" @change="onChange()">
            <option
                v-for="t in tournaments" :key="t._id.$oid"
                v-bind:value='t._id.$oid'> {{t.name}}
            </option>
        </select>
        <h3>Tournament Odds:</h3>
        <fixtures
            v-bind:fixtures="fixtures">
        </fixtures>
    </div>
</template>

<script>
import Vue from 'vue'
import { mapGetters } from "vuex";

import Fixtures from '@/components/Fixtures.vue'
import {
    SELECT_TOURNAMENT,
    FETCH_FIXTURES,
    FETCH_PPG_TABLE
} from '@/store/actions.type'

export default {
    name: 'Tournaments',

    computed: {
        ...mapGetters([
            "tournaments", "ppg_table",
            "selected_tournament", "fixtures"
        ])
    },

    data: function() {
        return {
            tournament: '',
            teams: []
        }
    },
    components: {
        Fixtures
    },

    methods: {
        /**
         * @desc pre-load tournament data
        */
        onChange() {
            this.$store.dispatch(SELECT_TOURNAMENT, this.tournament);

            this.$store.dispatch(FETCH_FIXTURES, this.selected_tournament);
            this.$store.dispatch(FETCH_PPG_TABLE, this.selected_tournament);

            this.$http.get(Vue.config.host + '/api/v1/team/' + this.selected_tournament)
                .then(function (response) {
                    this.teams = response.body.firstBatch;
                });
        }
    }
}
</script>
