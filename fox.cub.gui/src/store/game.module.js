import Vue from 'vue'

import {
    FETCH_GAMES
} from "./actions.type";

import {
    SET_HOME_GAMES,
    SET_AWAY_GAMES
} from "./mutations.type"

import Game, {Venue} from '@/models/Game';

const initialState = {
    // list of prev home team games
    home_games: [],
    // list of prev away team games
    away_games: []
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_GAMES](context, data) {
        let getGameUrl = `${Vue.config.host}/api/v1/game`;

        let params = { "team_id": data.team_id };
        if (data.tournament_id) params.tournament_id = data.tournament_id;

        Vue.http.get(getGameUrl, {params: params})
            .then(function (response) {
                if (data.venue == Venue.home) {
                    context.commit(SET_HOME_GAMES, response.body.firstBatch);
                } else if (data.venue == Venue.away) {
                    context.commit(SET_AWAY_GAMES, response.body.firstBatch);
                }
            });
    }
};

export const mutations = {
    [SET_HOME_GAMES](state, data) {
        state.home_games = Game.asFoxcub(data);
    },
    [SET_AWAY_GAMES](state, data) {
        state.away_games = Game.asFoxcub(data);
    }
};

const getters = {
    home_games(state) {
      return state.home_games;
    },
    away_games(state) {
        return state.away_games;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
