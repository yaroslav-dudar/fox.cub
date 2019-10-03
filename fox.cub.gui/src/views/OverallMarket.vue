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
            v-bind:fixtures="fixture_groups">
        </market-fixtures>
    </div>
</template>

<script>
import { mapGetters } from "vuex";

import MarketFixtures from '@/components/MarketFixtures.vue'
import {FixtureMixin} from '@/mixins/FixtureMixin'

import {
    FETCH_MARKET_FIXTURES
} from '@/store/actions.type'

export default {
    name: 'OverallMarket',

    mixins: [FixtureMixin],

    computed: {
        ...mapGetters([
            "market_tournaments", "fixtures"
        ])
    },

    data: function() {
        return {
            tournament: '',
            fixture_groups: {}
        }
    },
    components: {
        MarketFixtures
    },

    watch: {
        'fixtures': {
            handler: function() {
                this.fixture_groups = this.groupByDate();
            },
            deep: true
        }
    },

    methods: {
        onChange() {
            this.$store.dispatch(FETCH_MARKET_FIXTURES, this.tournament);
        }
    },

    created() {
        this.fixture_groups = this.groupByDate();
    }
}
</script>
