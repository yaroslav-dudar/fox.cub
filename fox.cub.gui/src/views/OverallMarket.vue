<template>
    <div>
        <form class="pure-form pure-form-stacked">
            <fieldset>
                <legend>Fixtures filtering</legend>
                <div class="pure-g">

                    <div class="pure-u-1 pure-u-md-1-3">
                        <label for="multi-sort">Sort By</label>
                        <select v-model="sort_by" class="pure-input-1-2" id="multi-sort">
                            <option v-bind:value='null'>---</option>
                            <option
                                v-for="s in sort_list" :key="s"
                                v-bind:value='s'> {{s}}
                            </option>
                        </select>
                    </div>

                    <div class="pure-u-1 pure-u-md-1-3">
                        <label for="multi-tournament">Tournament</label>
                        <select v-model="tournament_name"
                                @change="onChangeTournament()"
                                id="multi-tournament"
                                class="pure-input-1-2">

                            <option v-bind:value='null'>---</option>
                            <option
                                v-for="t in market_tournaments" :key="t"
                                v-bind:value='t'> {{t}}
                            </option>
                        </select>
                    </div>

                    <div class="pure-u-1 pure-u-md-1-3">
                        <label for="multi-team">Team</label>
                        <select v-model="team_name" class="pure-input-1-2" id="multi-team">
                            <option v-bind:value='null'>---</option>
                            <option
                                v-for="t in market_teams" :key="t"
                                v-bind:value='t'> {{t}}
                            </option>
                        </select>
                    </div>
                </div>
                <button type="button"
                        class="pure-button pure-button-primary"
                        v-on:click="onSubmit()">
                    Search</button>
            </fieldset>
        </form>

        <market-fixtures
            v-bind:fixtures="fixtures">
        </market-fixtures>
    </div>
</template>

<script>
import { mapGetters } from "vuex";

import MarketFixtures from '@/components/MarketFixtures.vue'
import {FixtureMixin} from '@/mixins/FixtureMixin'

import {
    FETCH_FIXTURES,
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
            tournament_name: null,
            team_name: null,
            sort_by: null,
            sort_list: ["homeDiff", "awayDiff"],
            fixture_groups: {}
        }
    },
    components: {
        MarketFixtures
    },

    methods: {
        onChangeTournament() {
            this.$store.dispatch(FETCH_MARKET_TEAMS,
                                 this.tournament_name);
        },
        onSubmit() {
            this.$store.dispatch(FETCH_FIXTURES, {
                tournament_name: this.tournament_name,
                team_name: this.team_name,
                sort_by: this.sort_by
            });
        }
    }
}
</script>
