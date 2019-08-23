import Vue from 'vue'

import {
    FETCH_TEAMS
} from "./actions.type";

import {
    SET_TEAMS
} from "./mutations.type"

const initialState = {
    teams: []
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_TEAMS](context, tournament_id) {
        var getTeamsUrl = `${Vue.config.host}/api/v1/team/${tournament_id}`;

        Vue.http.get(getOddsUrl)
            .then(function (response) {
                context.commit(SET_TEAMS, response.body.firstBatch)
            });
    }
};

export const mutations = {
    [SET_TEAMS](state, teams) {
        state.teams = teams;
    }
};

const getters = {
    teams(state) {
      return state.teams;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
