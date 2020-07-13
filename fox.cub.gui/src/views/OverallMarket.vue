<template>
    <div>
        <form class="pure-form pure-form-stacked market-form">
            <fieldset>
                <legend>Fixtures filtering</legend>
                <div class="pure-g">

                    <div class="pure-u-1 pure-u-md-1-2">
                        <label for="multi-sort">Sort By</label>
                        <select v-model="sort_by" class="pure-input-1-2" id="multi-sort">
                            <option v-bind:value='null'>---</option>
                            <option
                                v-for="s in sort_list" :key="s"
                                v-bind:value='s'> {{s}}
                            </option>
                        </select>
                    </div>

                    <div class="pure-u-1 pure-u-md-1-2">
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

                </div>
                <div class="pure-g">
                    <div class="pure-u-1 pure-u-md-1-2">
                        <label for="multi-team">Team</label>
                        <select v-model="team_name" class="pure-input-1-2" id="multi-team">
                            <option v-bind:value='null'>---</option>
                            <option
                                v-for="t in market_teams" :key="t"
                                v-bind:value='t'> {{t}}
                            </option>
                        </select>
                    </div>

                    <div class="pure-u-1 pure-u-md-1-2">
                        <label for="multi-date">Date Range</label>
                        <date-range-picker
                        style="float: left;"
                            class="pure-input-1-2" id="multi-date"
                            ref="picker"
                            v-model="dateRange"
                            :append-to-body="true"
                            :autoApply="true"
                            :locale-data="{
                                direction: 'ltr',
                                format: 'yyyy-mm-dd',
                                separator: ' - ',
                                applyLabel: 'Apply',
                                cancelLabel: 'Cancel',
                                weekLabel: 'W',
                                customRangeLabel: 'Custom Range',
                                firstDay: 0
                            }">
                        </date-range-picker>
                    </div>

                </div>
                <br>
                <div class="pure-g">
                    <button type="button"
                        class="pure-button pure-button-primary"
                        style="margin-right: 20px"
                        v-on:click="onSearchFixtures()">
                Search Fixtures</button>

                <button type="button"
                        v-on:click="onSearchMarketMoves()"
                        class="pure-button pure-button-primary"
                        >
                Show Market Movement</button>
                </div>

            </fieldset>
        </form>

        <div class="pure-g">
            <div class="pure-u-1 pure-u-md-1-2">
                <market-fixtures
                    :fixtures="fixtures">
                </market-fixtures>
            </div>
            <div class="pure-u-1 pure-u-md-1-2">
                <key-value-table
                    :table_data="market_moves"
                    :key_name="key_name"
                    :value_name="value_name">
                </key-value-table>
            </div>
        </div>
    </div>
</template>

<style lang="scss">

.market-form {
  background-color:#f8f9fa;
  border-color: #cbcbcb;
  border-style: solid;
  border-width: 1px;
  max-width: 50%;
  border-radius: 25px;
  padding: 25px;
}

</style>

<script>

import { mapGetters } from "vuex";
import DateRangePicker from 'vue2-daterange-picker';
import 'vue2-daterange-picker/dist/vue2-daterange-picker.css'

import MarketFixtures from '@/components/MarketFixtures.vue';
import KeyValueTable from '@/components/KeyValueTable.vue';
import {FixtureMixin} from '@/mixins/FixtureMixin';

import {
    FETCH_FIXTURES,
    FETCH_MARKET_MOVES,
    FETCH_MARKET_TEAMS
} from '@/store/actions.type'

export default {
    name: 'OverallMarket',

    mixins: [FixtureMixin],

    computed: {
        ...mapGetters([
            "market_tournaments", "fixtures",
            "market_teams", "market_moves"
        ])
    },

    data: function() {
        return {
            key_name: "Team Name",
            value_name: "Market movement %",
            tournament_name: null,
            team_name: null,
            dateRange: {
                startDate: this.getDateOffset(0),
                endDate: this.getDateOffset(10)
            },
            sort_by: null,
            sort_list: ["homeDiff", "awayDiff"],
            fixture_groups: {}
        }
    },
    components: {
        MarketFixtures,
        DateRangePicker,
        KeyValueTable
    },

    methods: {
        onChangeTournament() {
            this.$store.dispatch(FETCH_MARKET_TEAMS,
                                 this.tournament_name);
        },
        onSearchFixtures() {
            this.$store.dispatch(FETCH_FIXTURES, {
                tournament_name: this.tournament_name,
                team_name: this.team_name,
                sort_by: this.sort_by,
                start: this.dateToStr(this.dateRange.startDate),
                end: this.dateToStr(this.dateRange.endDate)
            });
        },

        onSearchMarketMoves() {
            this.$store.dispatch(FETCH_MARKET_MOVES, {
                start: this.dateToStr(this.dateRange.startDate),
                end: this.dateToStr(this.dateRange.endDate)
            });
        }
    }
}
</script>
