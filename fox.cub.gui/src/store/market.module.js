import Vue from 'vue'

import {
    FETCH_MARKET_TOURNAMENTS,
    FETCH_MARKET_MOVES,
    FETCH_MARKET_TEAMS
} from "./actions.type";

import {
    SET_MARKET_TOURNAMENTS,
    SET_MARKET_TEAMS,
    SET_MARKET_MOVES
} from "./mutations.type"

const initialState = {
    market_tournaments: [],
    market_teams: [],
    market_moves: {}
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_MARKET_TOURNAMENTS](context) {
        let getTournamentsUrl = `${Vue.config.host}/api/v1/market/tournaments`;

        Vue.http.get(getTournamentsUrl).then(function (response) {
            context.commit(SET_MARKET_TOURNAMENTS, response.body.values);
        });
    },
    async [FETCH_MARKET_TEAMS](context, tournament) {
        let getTeamsUrl = `${Vue.config.host}/api/v1/market/teams`;
        let params = { "tournament": tournament };

        Vue.http.get(getTeamsUrl, {params: params}).then(function (response) {
            context.commit(SET_MARKET_TEAMS, response.body.firstBatch);
        });
    },
    async [FETCH_MARKET_MOVES](context, data) {
        let getMovesUrl = `${Vue.config.host}/api/v1/market/movement`;

        Vue.http.get(getMovesUrl, {params: data}).then(function (response) {
            context.commit(SET_MARKET_MOVES, response.body);
        });
    }

};

export const mutations = {
    [SET_MARKET_TOURNAMENTS](state, tournaments) {
        state.market_tournaments = tournaments;
    },
    [SET_MARKET_TEAMS](state, teams) {
        state.market_teams = teams.length > 0 ? teams[0].teams: [];
    },
    [SET_MARKET_MOVES](state, data) {
        state.market_moves = data;
    },
};

const getters = {
    market_tournaments(state) {
      return state.market_tournaments;
    },
    market_teams(state) {
        return state.market_teams;
    },
    market_moves(state) {
        return state.market_moves;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
