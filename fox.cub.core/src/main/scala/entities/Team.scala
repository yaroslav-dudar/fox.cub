package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent

object Team {
    private val Collection = "team"

    def get(id: String): QueryEvent = {
        val filter = Json.obj(("_id", id))
        val query = new JsonObject().put("find", Collection).put("filter", filter)
        QueryEvent("find", query)
    }

    def getByTournament(tournamentId: String): QueryEvent = {
        val filter = Json.obj(("tournaments", tournamentId))
        val query = new JsonObject().put("find", Collection).put("filter", filter)
        QueryEvent("find", query)
    }
}
