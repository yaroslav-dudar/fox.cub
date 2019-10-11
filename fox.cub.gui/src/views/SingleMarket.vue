<template>
    <div>
        <h1>
            {{fixture.home_name}} vs {{fixture.away_name}}
        </h1>
        <div class="pure-g">
            <div class="pure-u-1-1">
                <odds-movement v-bind:odds_diff="odds_diff"> </odds-movement>
            </div>
        </div>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <time-series-chart
                    v-bind:data="timeline.home" title="Home Win">
                </time-series-chart>
            </div>
            <div class="pure-u-1-3">
                <time-series-chart
                    v-bind:data="timeline.away" title="Away Win">
                </time-series-chart>
            </div>
            <div class="pure-u-1-3">
                <time-series-chart
                    v-bind:data="timeline.draw" title="Draw">
                </time-series-chart>
            </div>
        </div>
        <div class="pure-g">
            <div class="pure-u-1-2">
                <time-series-chart
                    v-bind:data="timeline.over" title="Over Goals">
                </time-series-chart>
            </div>
            <div class="pure-u-1-2">
                <time-series-chart
                    v-bind:data="timeline.under" title="Under Goals">
                </time-series-chart>
            </div>
        </div>
    </div>
</template>

<script>
import { mapGetters } from "vuex";

import TimeSeriesChart from '@/components/TimeSeriesChart.vue'
import OddsMovement from '@/components/OddsMovement.vue'
import {OddsMixin} from '@/mixins/OddsMixin'

import {
    FETCH_ODDS,
    FETCH_ODDS_DIFF
} from '@/store/actions.type'

export default {
    name: 'SingleMarket',

    mixins: [OddsMixin],

    computed: {
        ...mapGetters([
            "market_tournaments", "fixtures",
            "odds", "odds_diff"
        ])
    },

    data: function() {
        return {
            fixture: {},
            tournament: '',
            timeline: {
                home: [], away: [],
                draw: [], over: [],
                under: []
            }
        }
    },
    components: {
        TimeSeriesChart,
        OddsMovement
    },

    created: function() {
        let fixture_id = this.$route.query.fixture;
        this.fixture = this.fixtures.find(f => f._id.$oid == fixture_id);
        this.tournament = this.fixture.tournament_id;

        this.$store.dispatch(FETCH_ODDS, this.fixture.external_ids);
        this.$store.dispatch(FETCH_ODDS_DIFF, this.fixture.external_ids);
    },

    watch: {
        'odds': {
            handler: function() {
                this.timeline.home = this.getMoneylineSeries("home");
                this.timeline.away = this.getMoneylineSeries("away");
                this.timeline.draw = this.getMoneylineSeries("draw");

                this.timeline.over = this.getTotalSeries("over");
                this.timeline.under = this.getTotalSeries("under");
            },
            deep: true
        }
    },

    methods: {}
}
</script>
