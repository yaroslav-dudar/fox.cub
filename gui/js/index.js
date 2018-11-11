var host = "http://localhost:8888";

// define component

var TournamentsComponent = {
    data: function() {
        return {
            tournaments: [],
            tournament: '',
            odds: [],
            teams: []
        }
    },
    template: `
    <div>
        <h3>Select Tournament</h3>
        <select v-model="tournament" @change="onChange()">
            <option 
                v-for="t in $store.state.tournaments"
                v-bind:value='t._id["$oid"]'> {{t.name}}
            </option>
        </select>
        <h3>Tournament Odds:</h3>
        <tournament-odds v-bind:odds="$store.state.odds"></tournament-odds>
    </div>
    `,
    created: function() {
        this.tournament = this.$store.state.tournament;
    },
    methods: {
        onChange(resource) {
            this.$store.commit('setCurrentTournament', this.tournament)

            this.$http.get(host + '/api/v1/team/' + this.tournament)
                .then(function (response) {
                    this.teams = response.body.firstBatch;
                });
    
            this.$http.get(host + '/api/v1/odds/' + this.tournament)
                .then(function (response) {
                    this.odds = response.body.firstBatch;
                    this.$store.commit('setOdds', this.odds)
                });
        }
    }
}

var CustomGameComponent = {
    template: `
    <div>
        <h3>Select Home Team</h3>
        <select v-model="home_team">
            <option 
                v-for="t in teams"
                v-bind:value='t._id["$oid"]'> {{t.name}}
            </option>
        </select>

        <h3>Select Away Team</h3>
        <select v-model="away_team">
            <option 
                v-for="t in teams"
                v-bind:value='t._id["$oid"]'> {{t.name}}
            </option>
        </select>
        <button v-on:click="getStats">Get Stats</button>
    </div>
    `
}

var GameComponent = {
    data: function() {
        return {
            home_team: '',
            away_team: '',
            tournament: '',
            home_team_games: [],
            away_team_games: [],
            stats: {},
            odd_list: []
        }
    },
    template: `
    <div>
        <div class="pure-g pure-u-1 center">
        <h1>
        <a v-on:click="redirectToTeam(home_team)">{{game_odds.home_team[0].name}}</a> vs 
        <a v-on:click="redirectToTeam(away_team)">{{game_odds.away_team[0].name}}</a>
        </h1>
        </div>
        <div class="pure-g">
            <div class="pure-u-1-3">
                <h3>Home Team Results:</h3>
                <team-results v-bind:games="home_team_games"></team-results>
            </div>
            <div class="pure-u-1-3">
                <h3>Away Team Results:</h3>
                <team-results v-bind:games="away_team_games"></team-results>
            </div>
            <div class="pure-u-1-3">
                <h3>Game Odds History:</h3>
                <game-odds v-bind:odds_history="game_odds.odds"></game-odds>
            </div>
        </div>
        <div class="pure-g pure-u-1">
            <h3>Calculated probabilities:</h3>
            <pre v-html="stats"></pre>
        </div>
    </div>`,

    created: function() {
        this.home_team = this.$route.query.home_team;
        this.away_team = this.$route.query.away_team;
        this.tournament = this.$route.query.tournament;
        this.game_odds = this.$store.state.odds[this.$route.query.odd_index];

        this.getGames();
        this.getStats();
    },

    methods: {
        getStats(event) {
            if (!this.home_team || !this.away_team) {
                alert("Select rivals!");
                return;
            }

            var query = {
                home_team_id: this.home_team,
                away_team_id: this.away_team
            };

            this.$http.get(host + '/api/v1/stats/' + this.tournament, {params: query})
                .then(function (response) {
                    this.stats = response.body;
                });

            this.getGames();
        },
        getGames() {
            var home_team_q = {
                "team_id": this.home_team,
                "tournament_id": this.tournament
            };

            var away_team_q = {
                "team_id": this.away_team,
                "tournament_id": this.tournament
            };
        
            this.$http.get(host + '/api/v1/game', {params: home_team_q})
                .then(function (response) {
                    this.home_team_games = response.body.firstBatch;
                });

            this.$http.get(host + '/api/v1/game', {params: away_team_q})
                .then(function (response) {
                    this.away_team_games = response.body.firstBatch;
                });
        },
        redirectToTeam(team_id) {
            router.push({path: '/team', query: { team: team_id }})
        }
    }
}

var TeamResultsComponent = Vue.component('team-results', {
    props: ['games'],
    template: `
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Home Team</th>
                <th>Score</th>
                <th>Away Team</th>
            </tr>
        </thead>
        <tr v-for="g in games">
            <td v-if="g.venue == 'home'"><strong>{{g.team[0].name}}</strong></td>
            <td v-else>{{g.opponent[0].name}}</td>

            <td v-if="g.venue == 'home'">{{g.goals_for}} - {{g.goals_against}}</td>
            <td v-else>{{g.goals_against}} - {{g.goals_for}}</td>

            <td v-if="g.venue == 'home'">{{g.opponent[0].name}}</td>
            <td v-else><strong>{{g.team[0].name}}</strong>
            </td>
        </tr>
    </table>
    `
})

var GameOddsHistory = Vue.component('game-odds', {
    props: ['odds_history'],
    template: `
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Home Win</th>
                <th>Draw</th>
                <th>Away Win</th>
                <th>Total</th>
                <th>Total Under</th>
                <th>Total Over</th>
                <th>Scraping Date</th>
            </tr>
        </thead>
        <tr v-for="o in odds_history">
            <td>{{o.home_win}}</td>
            <td>{{o.draw}}</td>
            <td>{{o.away_win}}</td>
            <td>{{o.total}}</td>
            <td>{{o.total_under}}</td>
            <td>{{o.total_over}}</td>
            <td>{{o.scraping_date.$date}}</td>
        </tr>
    </table>
    `
});

var TournamentOddsComponent = Vue.component('tournament-odds', {
    props: ['odds'],
    template: `
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Home Team</th>
                <th>Away Team</th>
                <th>Home Win</th>
                <th>Draw</th>
                <th>Away Win</th>
                <th>Total</th>
                <th>Total Under</th>
                <th>Total Over</th>
                <th>Event Date</th>
                <th>Detail Stats</th>
            </tr>
        </thead>
        <tr v-for="(o,i) in odds">
            <td>{{o.home_team[0].name}}</td>
            <td>{{o.away_team[0].name}}</td>
            <td>{{o.odds[o.odds.length-1].home_win}}</td>
            <td>{{o.odds[o.odds.length-1].draw}}</td>
            <td>{{o.odds[o.odds.length-1].away_win}}</td>
            <td>{{o.odds[o.odds.length-1].total}}</td>
            <td>{{o.odds[o.odds.length-1].total_under}}</td>
            <td>{{o.odds[o.odds.length-1].total_over}}</td>
            <td>{{o.event_date.$date}}</td>
            <td><button
                v-on:click="redirectToGame(
                    o.home_team[0]._id['$oid'],
                    o.away_team[0]._id['$oid'],
                    o.tournament, i)">
            Get Stats</button></td>
        </tr>
    </table>
    `,
    methods: {
        redirectToGame(home_team, away_team, tournament, indx) {
            router.push({
                path: 'game', query: {
                    home_team: home_team,
                    away_team: away_team,
                    tournament: tournament,
                    odd_index: indx
                }
            })
        }
    }
})

var TeamComponent = {
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
    template: `
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
                    <option v-for="type in note_types" v-bind:value="type">
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
            <li v-for="note in notes_list">
                {{ note.note_text }} {{ note.created_at.$date }}
            </li>
        </ul>
    </div>
    `,
    created: function() {
        this.team_id = this.$route.query.team;
        this.new_note.ref_id = this.team_id;
        this.getUserNotes();
    },

    methods: {
        addUserNote() {
            var endpoint = host + '/api/v1/note';

            return this.$http.post(endpoint, this.new_note)
                .then(function (response) {
                    // reset note text
                    this.new_note.note_text = "";
                    this.getUserNotes();
                }).catch(function(error) {
                    alert(JSON.stringify(error.body));
                })
        },
        getUserNotes(event) {
            var endpoint = host + '/api/v1/note/' + this.team_id;
            var query = {user_id: "1", ref_to: "team"};

            return this.$http.get(endpoint, {params: query})
                .then(function (response) {
                    this.notes_list = response.body.firstBatch;
                });
        }
    }
}

const router = new VueRouter({
    routes: [
        { path: '/', component: TournamentsComponent, props: true },
        { path: '/game', component: GameComponent, props: true },
        { path: '/team', component: TeamComponent, props: true }
    ]
})

const store = new Vuex.Store({
    state: {
        tournaments: [],
        tournament: '',
        odds: [],
        teams: []
    },
    mutations: {
        setTournaments: function(state, tournaments) {
            state.tournaments = tournaments;
        },
        setOdds: function(state, odds) {
            state.odds = odds;
        },
        setCurrentTournament: function(state, tournament) {
            state.tournament = tournament;
        }
    }
})

// root component
var app = new Vue({
    router: router,
    store: store,
    el: '#app',

    methods: {
        getTournaments: function() {
            return this.$http.get(host + '/api/v1/tournament')
                .then(function (response) {
                    return response.body.firstBatch;
                });
        }
    },
    created: function () {
        this.getTournaments().then(function(data) {
            this.$store.commit('setTournaments', data);
        })
    }
});
