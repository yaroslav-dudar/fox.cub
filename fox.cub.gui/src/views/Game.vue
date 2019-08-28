<template>
    <div>
        <div class="pure-g pure-u-1 center">
        <h1>
        <a v-on:click="redirectToTeam(home_team)">{{fixture.home_name}}</a> vs
        <a v-on:click="redirectToTeam(away_team)">{{fixture.away_name}}</a>
        </h1>
        </div>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <h3>Home Team Results:</h3>
                <team-results v-bind:games="home_games_to_view"></team-results>
            </div>
            <div class="pure-u-1-3">
                <h3>Away Team Results:</h3>
                <team-results v-bind:games="away_games_to_view"></team-results>
            </div>
            <div class="pure-u-1-3">
                <h3>Game Odds History:</h3>
                <game-odds v-bind:odds_history="odds"></game-odds>
            </div>
        </div>
        <br>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <team-stats v-bind:games="home_games_to_view"> </team-stats>
                <last-games-chart
                    v-bind:games="home_games_to_view"
                    v-bind:team_name="fixture.home_team">
                </last-games-chart>
            </div>
            <div class="pure-u-1-3">
                <team-stats v-bind:games="away_games_to_view"> </team-stats>
                <last-games-chart
                    v-bind:games="away_games_to_view"
                    v-bind:team_name="fixture.away_team">
                </last-games-chart>

            </div>
        </div>
        <br>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <rolling-trend-chart
                    v-bind:games="home_games_to_view"
                    v-bind:team_name="fixture.home_team"
                    v-bind:type="settings.rolling_trend.type"
                    v-bind:size="settings.rolling_trend.size">
                </rolling-trend-chart>
            </div>
            <div class="pure-u-1-3">
                <rolling-trend-chart
                    v-bind:games="away_games_to_view"
                    v-bind:team_name="fixture.away_team"
                    v-bind:type="settings.rolling_trend.type"
                    v-bind:size="settings.rolling_trend.size">
                </rolling-trend-chart>
            </div>
        </div>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <schedule-chart
                    v-bind:ppg_table="ppg_table"
                    v-bind:games="home_games_to_view"
                    v-bind:size="settings.rolling_trend.size">
                </schedule-chart>
            </div>
            <div class="pure-u-1-3">
                <schedule-chart
                    v-bind:ppg_table="ppg_table"
                    v-bind:games="away_games_to_view"
                    v-bind:size="settings.rolling_trend.size">
                </schedule-chart>
            </div>
        </div>
        <div>
            <app-settings
                v-bind:settings="settings"
                v-on:reset="resetFilters">
            </app-settings>
        </div>
        <div class="pure-g pure-u-1">
            <h3>Calculated probabilities:</h3>
            <pre v-html="stats"></pre>
        </div>
    </div>
</template>

<script>
import { mapGetters } from "vuex";
import router from '@/router'

import GameOdds from '@/components/GameOdds.vue'
import TeamResults from '@/components/TeamResults.vue'
import TeamStats from '@/components/TeamStats.vue'
import AppSettings from '@/components/AppSettings.vue'

import ScheduleChart from '@/components/ScheduleChart.vue'
import RollingTrendChart from '@/components/RollingTrendChart.vue'
import LastGamesChart from '@/components/LastGamesChart.vue'

import {
    FETCH_GAMES,
    FETCH_ODDS,
    FETCH_STATS
} from '@/store/actions.type'


export default {
    computed: {
        ...mapGetters([
            "home_games", "away_games", "odds",
            "ppg_table", "fixtures", "stats"
        ])
    },

    data: function() {
        return {
            home_team: '',
            away_team: '',
            tournament: '',
            fixture: {},
            home_games_to_view: [], // home games with applied filters
            away_games_to_view: [], // away games with applied filters
            settings: {
                full_history: true,
                rolling_trend: {
                    type: 'xG', // allowed [xG, goals]
                    size: 6
                },
                away_home_filter: false,
                reset_selected: false
            }
        }
    },
    components: {
        GameOdds,
        TeamResults,
        TeamStats,
        AppSettings,
        LastGamesChart,
        ScheduleChart,
        RollingTrendChart
    },
    created: function() {
        let fixture_id = this.$route.query.fixture;

        this.fixture = this.fixtures.find(f => f._id.$oid == fixture_id);
        this.home_team = this.fixture.home_id.$oid;
        this.away_team = this.fixture.away_id.$oid;
        this.tournament = this.fixture.tournament_id;

        this.fetchGames();
        this.applyHomeGameFilters();
        this.applyAwayGameFilters();

        this.$store.dispatch(FETCH_ODDS, this.fixture.external_ids);
        this.$store.dispatch(FETCH_STATS, {
            home_team_id: this.home_team,
            away_team_id: this.away_team,
            tournament_id: this.tournament
        });
    },

    watch: {
        home_games() { this.applyHomeGameFilters() },
        away_games() { this.applyAwayGameFilters() },
        'settings.full_history': {
            handler: function() { this.fetchGames() },
            deep: true
        },
        'settings.away_home_filter': {
            handler: function() {
                this.resetFilters()
            },
            deep: true
        }
    },
    methods: {
        resetFilters() {
            this.applyHomeGameFilters();
            this.applyAwayGameFilters();
        },
        applyHomeGameFilters() {
            var games = this.home_games.filter((g) => {
                if (this.settings.away_home_filter) {
                    return g.venue == "home";
                }
                return true;
            }).filter((g) => {
                if (g.tournament == this.tournament) {
                    g.selected = true;
                } else {
                    g.selected = false;
                }
                return true;
            });
            this.home_games_to_view = games;
        },
        applyAwayGameFilters() {
            var games = this.away_games.filter((g) => {
                if (this.settings.away_home_filter) {
                    return g.venue == "away";
                }
                return true;
            }).filter((g) => {
                if (g.tournament == this.tournament) {
                    g.selected = true;
                } else {
                    g.selected = false;
                }
                return true;
            });
            this.away_games_to_view = games;
        },

        fetchGames() {
            this.$store.dispatch(FETCH_GAMES,
                {
                    team_id: this.home_team,
                    tournament_id: this.settings.full_history ? null : this.tournament,
                    venue: 'home'
                });

            this.$store.dispatch(FETCH_GAMES,
                {
                    team_id: this.away_team,
                    tournament_id: this.settings.full_history ? null : this.tournament,
                    venue: 'away'
                });
        },

        redirectToTeam(team_id) {
            router.push({path: '/team', query: { team: team_id }})
        }
    }
}
</script>
