<template>
    <div>
        <h3>Select Tournament</h3>
        <select v-model="tournament" @change="onChange()">
            <option
                v-for="t in tournaments" :key="t._id.$oid"
                v-bind:value='t._id.$oid'> {{t.name}}
            </option>
        </select>
        <h3>Tournament Fixtures:</h3>
        <fixtures
            v-bind:fixtures="fixtures">
        </fixtures>
    </div>
</template>

<script>
import { mapGetters } from "vuex";

import Fixtures from '@/components/Fixtures.vue'
import {
    SELECT_TOURNAMENT,
    FETCH_FIXTURES,
    FETCH_TEAMS
} from '@/store/actions.type'

export default {
    name: 'Tournaments',

    computed: {
        ...mapGetters([
            "tournaments", "ppg_table",
            "selected_tournament", "fixtures",
            "teams"
        ])
    },

    data: function() {
        return {
            tournament: ''
        }
    },
    components: {
        Fixtures
    },

    methods: {
        /**
         * @desc pre-load tournament related data
        */
        onChange() {
            this.$store.dispatch(SELECT_TOURNAMENT, this.tournament);
            this.$store.dispatch(FETCH_FIXTURES, this.selected_tournament);
            this.$store.dispatch(FETCH_TEAMS, this.selected_tournament);
        }
    }
}
</script>
