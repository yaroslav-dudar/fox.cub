package fox.cub.model

import scala.collection.mutable.Buffer

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent
import fox.cub.utils.Utils.getUTCdate

object Odds {
    private val Collection = "odds"

    /**
     * Get odds timeline for fixture
     * @param fixtureIds External fixture ids
    */

    def get(fixtureIds: Buffer[Int]): QueryEvent = {
        val filter = Json.obj(("fixture_id",
                               Json.obj(("$in", fixtureIds))))

        val query = new JsonObject().put("find", Collection).put("filter", filter)
        QueryEvent("find", query)
    }
}
