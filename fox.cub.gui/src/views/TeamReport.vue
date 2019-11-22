<template>
    <div class="pure-g">
        <div class="pure-u-1-2">
            <team-results v-bind:games="home_games"></team-results>
        </div>
        <div class="pure-u-1-2">

            <form class="pure-form pure-form-stacked" style="text-align:left;">
                <label for="select_league">Select Tournament</label>
                <select
                    v-model="tournament"
                    @change="onChangeTournament()"
                    id="select_league">

                    <option
                        v-for="t in tournaments" :key="t._id.$oid"
                        v-bind:value='t._id.$oid'> {{t.name}}
                    </option>
                </select>

                <label for="select_team">Select Team</label>
                <select
                    v-model="team_id"
                    @change="onChangeTeam()"
                    id="select_team">

                    <option
                        v-for="t in teams" :key="t._id.$oid"
                        v-bind:value='t._id.$oid'> {{t.name}}
                    </option>
                </select>
            </form>

            <detailed-team-stats v-bind:games="home_games"
                v-bind:home_adv="home_adv">
            </detailed-team-stats>

            <form class="pure-form pure-form-stacked" style="text-align:left;">
                <fieldset>
                    <legend>Add New Team Note</legend>
                    <div class="pure-control-group">
                        <label for="name">Note Text</label>
                        <textarea v-model="new_note.note_text" placeholder="Add some text" rows="4" cols="50"></textarea>
                    </div>

                    <div class="pure-control-group">
                        <label for="password">Note Category</label>
                        <select v-model="new_note.note_type">
                            <option
                                v-for="(type,i) in note_types"
                                :key="i" v-bind:value="type">
                                {{ type }}
                            </option>
                        </select>
                    </div>

                    <div class="pure-controls">
                        <button
                            type="submit"
                            class="pure-button pure-button-primary"
                            v-on:click="addUserNote()">Submit</button>
                    </div>
                </fieldset>
            </form>

            <ul>
                <li v-for="note in notes_list" :key="note._id.$oid">
                    {{ note.note_text }} {{ note.created_at.$date }}
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
import { mapGetters } from "vuex";
import Vue from 'vue'

import TeamResults from '@/components/TeamResults.vue'
import DetailedTeamStats from '@/components/DetailedTeamStats.vue'

import {
    SELECT_TOURNAMENT,
    FETCH_GAMES,
    FETCH_TEAMS,
    FETCH_HOME_ADV
} from '@/store/actions.type'

export default {
    components: {
        TeamResults,
        DetailedTeamStats
    },
    computed: {
        ...mapGetters([
            "tournaments", "ppg_table", "home_games",
            "selected_tournament", "teams", "home_adv"
        ])
    },
    data: function() {
        return {
            team_id: '',
            notes_list: [],
            tournament: '',
            note_types: ["review", "weakness", "strength", "general"],
            new_note: {
                note_text: '',
                ref_to: 'team',
                note_type: '',
                ref_id: ''
            }
        }
    },
    created: function() {
        this.init();
        this.applyTeamFilters();
    },

    watch: {
        home_games() { this.applyTeamFilters() },
    },

    methods: {
        init: function() {
            this.team_id = this.$route.query.team;
            if (this.team_id) {
                this.new_note.ref_id = this.team_id;
                this.getUserNotes();
            }
        },
        addUserNote() {
            var endpoint = Vue.config.host + '/api/v1/note';

            return this.$http.post(endpoint, this.new_note)
                .then(function () {
                    // reset note text
                    this.new_note.note_text = "";
                    this.getUserNotes();
                }).catch(function(error) {
                    alert(JSON.stringify(error.body));
                })
        },
        getUserNotes() {
            var endpoint = Vue.config.host + '/api/v1/note/' + this.team_id;
            var query = {user_id: "1", ref_to: "team"};

            return this.$http.get(endpoint, {params: query})
                .then(function (response) {
                    this.notes_list = response.body.firstBatch;
                });
        },
        /**
         * @desc pre-load tournament related data
        */
        onChangeTournament() {
            this.$store.dispatch(SELECT_TOURNAMENT, this.tournament);
            this.$store.dispatch(FETCH_TEAMS, this.selected_tournament);
            this.$store.dispatch(FETCH_HOME_ADV, this.selected_tournament);
        },
        onChangeTeam() {
            this.$store.dispatch(FETCH_GAMES,
                {
                    team_id: this.team_id,
                    tournament_id: null,
                    venue: 'home'
                });
        },
        applyTeamFilters() {
            this.home_games.filter((g) => {
                if (g.tournament == this.tournament) {
                    g.selected = true;
                } else {
                    g.selected = false;
                }
                return true;
            });
        }
    }
}
</script>
