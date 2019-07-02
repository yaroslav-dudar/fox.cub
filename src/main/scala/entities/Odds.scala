package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent
import fox.cub.utils.Utils.getUTCdate

object Odds {
    private val Collection = "odds"

    /**
     * Get odds timeline for fixture
     * @param fixtureId Fixture id
    */

    def get(fixtureId: Int): QueryEvent = {
        val filter = Json.obj(("fixture_id", fixtureId))
        val query = new JsonObject().put("find", Collection).put("filter", filter)
        QueryEvent("find", query)
    }
}
