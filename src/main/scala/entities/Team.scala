package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent

object Team {
    private val Collection = "team"

    def get(name: String): QueryEvent = {
        val nameFilter = Json.obj(("name", Json.obj(("$eq", name))))
        val query = new JsonObject().put("find", Collection).put("filter", nameFilter)
        QueryEvent("find", query)
    }
}
