<template>
    <div>
        <h3>Select Tournament</h3>
        <select v-model="tournament" @change="onChangeTournament()">
            <option
                v-for="t in market_tournaments" :key="t"
                v-bind:value='t'> {{t}}
            </option>
        </select>
        <hr>
        <select v-model="team" @change="onChangeTeam()">
            <option
                v-for="t in market_teams" :key="t"
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
    FETCH_MARKET_FIXTURES,
    FETCH_MARKET_TEAMS
} from '@/store/actions.type'

export default {
    name: 'OverallMarket',

    mixins: [FixtureMixin],

    computed: {
        ...mapGetters([
            "market_tournaments", "fixtures",
            "market_teams"
        ])
    },

    data: function() {
        return {
            tournament: '',
            team: '',
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
        onChangeTournament() {
            this.$store.dispatch(FETCH_MARKET_TEAMS, this.tournament);
        },
        onChangeTeam() {
            this.$store.dispatch(FETCH_MARKET_FIXTURES, {
                tournament: this.tournament,
                team: this.team
            });
        }
    },

    created() {
        this.fixture_groups = this.groupByDate();
    }
}
</script>
