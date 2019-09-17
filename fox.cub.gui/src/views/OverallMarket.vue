<template>
    <div>
        <h3>Select Tournament</h3>
        <select v-model="tournament" @change="onChange()">
            <option
                v-for="t in market_tournaments" :key="t"
                v-bind:value='t'> {{t}}
            </option>
        </select>
        <market-fixtures
            v-bind:fixtures="fixtures">
        </market-fixtures>
    </div>
</template>

<script>
import { mapGetters } from "vuex";

import MarketFixtures from '@/components/MarketFixtures.vue'
import {
    FETCH_MARKET_FIXTURES
} from '@/store/actions.type'

export default {
    name: 'OverallMarket',

    computed: {
        ...mapGetters([
            "market_tournaments", "fixtures"
        ])
    },

    data: function() {
        return {
            tournament: ''
        }
    },
    components: {
        MarketFixtures
    },

    methods: {
        onChange() {
            this.$store.dispatch(FETCH_MARKET_FIXTURES, this.tournament);
        }
    }
}
</script>
