package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject
import fox.cub.internals.QueryEvent
import fox.cub.utils.Utils.getUTCdate


object User {
    private val Collection = "user"

    /**
     * Add given fixture to the favorite list,
     * so it may be tracked easely
     * @param note data in JSON fromat
    */
    def addFavFixture(data: JsonObject): QueryEvent = {
        var createdAt = Json.obj(("$date", getUTCdate()))

        val q = Json.obj(("_id", Json.obj(("$oid", data.getString("user")))))
        val push = Json.obj( ("fav_fixtures", data.getString("fixture")) )
        val u = Json.obj(("$push", push))
        val update = Json.obj(
            ("u", u),
            ("q", q),
            ("upsert", false),
            ("multi", false)
        )

        val query = new JsonObject()
            .put("update", Collection)
            .put("updates", Json.arr(update))

        QueryEvent("update", query)
    }

    def findUser(username: String): QueryEvent = {
        val filter = Json.obj(("username", username))
        val query = new JsonObject().put("find", Collection).put("filter", filter)
        QueryEvent("find", query)
    }

    def getUser(res: JsonObject): Option[JsonObject] = {
        val arr = res.getJsonArray("firstBatch")
        if (arr.size != 1) None
        else Some(res.getJsonArray("firstBatch").getJsonObject(0))
    }
}
