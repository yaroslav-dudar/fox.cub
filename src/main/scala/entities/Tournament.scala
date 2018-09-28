package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent

object Tournament {
    private val Collection = "tournament"

    def getAll(): QueryEvent = {
        val query = new JsonObject().put("find", Collection)
        QueryEvent("find", query)
    }
}
