import Vue from 'vue'

import {
    FETCH_STATS,
    FETCH_MANUAL_STATS
} from "./actions.type";

import {
    SET_STATS
} from "./mutations.type"

const initialState = {
    stats: {}
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_STATS](context, data) {
        let getStatsUrl = `${Vue.config.host}/api/v1/stats/${data.tournament_id}`;

        var params = {
            home_team_id: data.home_team_id,
            away_team_id: data.away_team_id
        };

        Vue.http.get(getStatsUrl, {params: params})
            .then(function (response) {
                context.commit(SET_STATS, response.body)
            });
    },

    async [FETCH_MANUAL_STATS](context, data) {
        var params = {tournament_id: data.tournament_id};

        let getManualStatsUrl = `${Vue.config.host}/api/v1/model/stats`;

        let bodyData = {
            firstBatch: [{
                tournament_avg: [{
                    avgScoredHome: parseFloat(data.tournament_avg_score/2),
                    avgScoredAway: parseFloat(data.tournament_avg_score/2)
                }],
                home_team: [{
                    scored_xg: [parseFloat(data.home_attack)],
                    conceded_xg: [parseFloat(data.home_defend)]
                }],
                away_team: [{
                    scored_xg: [parseFloat(data.away_attack)],
                    conceded_xg: [parseFloat(data.away_defend)]
                }]
            }]
        };

        Vue.http.post(getManualStatsUrl, bodyData, {params: params})
            .then(function (response) {
                context.commit(SET_STATS, response.body)
            });
    }
};

export const mutations = {
    [SET_STATS](state, stats) {
        state.stats = stats;
    }
};

const getters = {
    stats(state) {
      return state.stats;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
