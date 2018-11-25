<template>
    <div>
        <form class="pure-form pure-form-aligned">
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
</template>

<script>
import Vue from 'vue'

export default {
    data: function() {
        return {
            team_id: '',
            notes_list: [],
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
        this.team_id = this.$route.query.team;
        this.new_note.ref_id = this.team_id;
        this.getUserNotes();
    },
    methods: {
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
        }
    }
}
</script>
