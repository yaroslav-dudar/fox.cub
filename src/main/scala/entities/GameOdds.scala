package fox.cub.model

import java.text.SimpleDateFormat
import java.util.TimeZone

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent

object GameOdds {
    private val Collection = "game_odds"

    /**
     * Get list of not expired game odds
    */
    def getRecent(tournamentId: String): QueryEvent = {
        val dateFormat = "yyyy-MM-dd'T'HH:mm:ssXXX"
        val dateFilter = Json.obj(("$gt", Json.obj(("$date", _getUTCdate(dateFormat)))))

        val aggMatch = Json.obj(
            ("$match", Json.obj(
                ("tournament", tournamentId),
                ("event_date", dateFilter)
            )))

        val teamsToObjects =  Json.obj(("$addFields", Json.obj(
                ("home_team", Json.obj(("$toObjectId", "$home_team"))),
                ("away_team", Json.obj(("$toObjectId", "$away_team")))
            )))

        val joinHomeTeam = Json.obj(("$lookup", Json.obj(
            ("from", "team"),
            ("localField", "home_team"),
            ("foreignField", "_id"),
            ("as", "home_team")
            )))

        val joinAwayTeam = Json.obj(("$lookup", Json.obj(
            ("from", "team"),
            ("localField", "away_team"),
            ("foreignField", "_id"),
            ("as", "away_team")
            )))

        var pipeline = Json.arr(aggMatch, teamsToObjects, joinHomeTeam, joinAwayTeam)
        // cursor with the default batch size
        var cursor = Json.obj()
        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }

    def _getUTCdate(dateFormat: String) = {
        val df = new SimpleDateFormat(dateFormat)
        df.setTimeZone(TimeZone.getTimeZone("UTC"))
        df.format(System.currentTimeMillis)
    }

}
