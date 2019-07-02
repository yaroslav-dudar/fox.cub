package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent
import fox.cub.utils.Utils.getUTCdate

object Fixtures {
    private val Collection = "fixtures"

    /**
     * Get list of not expired fixtures
     * @param tournamentId Fixtures belongs to a tournament
    */

    def getRecent(tournamentId: Option[String]): QueryEvent = {
        val dateFilter = Json.obj(("$gt", Json.obj(("$date", getUTCdate()))))

        val aggMatch = Json.obj(
            ("$match", Json.obj( ("date", dateFilter) )))

        val sort = Json.obj(
            ("$sort", Json.obj( ("date", 1) )))

        if (tournamentId != None)
            // search by tournament
            aggMatch.getJsonObject("$match").put("tournament_id", tournamentId.get)

        val teamsToObjects =  Json.obj(("$addFields", Json.obj(
                ("home_id", Json.obj(("$toObjectId", "$home_id"))),
                ("away_id", Json.obj(("$toObjectId", "$away_id")))
            )))

        val joinHomeTeam = Json.obj(("$lookup", Json.obj(
            ("from", "team"),
            ("localField", "home_id"),
            ("foreignField", "_id"),
            ("as", "home_team")
            )))

        val joinAwayTeam = Json.obj(("$lookup", Json.obj(
            ("from", "team"),
            ("localField", "away_id"),
            ("foreignField", "_id"),
            ("as", "away_team")
            )))

        var pipeline = Json.arr(aggMatch, sort, teamsToObjects, joinHomeTeam, joinAwayTeam)
        var cursor = Json.obj()

        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }
}
