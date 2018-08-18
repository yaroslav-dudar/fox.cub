package fox.cub.model

import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent

object GameStats {
    private val Collection = "game_stats"

    def get(id: String): QueryEvent = {
        val query = new JsonObject().put("find", Collection).put("_id", id)
        QueryEvent("find", query)
    }

    def get(home: String, away: String) {
        
    }
}
