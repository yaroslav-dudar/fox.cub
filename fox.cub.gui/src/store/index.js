import Vue from "vue";
import Vuex from "vuex";

import fixture from "./fixture.module";
import odd from "./odd.module";
import tournament from "./tournament.module";
import game from "./game.module";
import stats from "./stats.module";

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    tournament,
    fixture,
    odd,
    game,
    stats
  }
});
