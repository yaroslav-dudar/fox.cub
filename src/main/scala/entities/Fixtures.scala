package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent
import fox.cub.utils.Utils.{getUTCdate, getDateByMillis}

object Fixtures {
    private val Collection = "fixtures"

    private val teamsToObjects =  Json.obj(("$addFields", Json.obj(
                ("home_id", Json.obj(("$toObjectId", "$home_id"))),
                ("away_id", Json.obj(("$toObjectId", "$away_id")))
            )))

    private val joinHomeTeam = Json.obj(("$lookup", Json.obj(
            ("from", "team"),
            ("localField", "home_id"),
            ("foreignField", "_id"),
            ("as", "home_team")
            )))

    private val joinAwayTeam = Json.obj(("$lookup", Json.obj(
            ("from", "team"),
            ("localField", "away_id"),
            ("foreignField", "_id"),
            ("as", "away_team")
            )))
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

    /**
     * Get list of available tournaments among all fixtures
    */
    def getTournaments(): QueryEvent = {
        val distinct = new JsonObject().put("distinct", Collection).
            put("key", "tournament_name")

        QueryEvent("distinct", distinct)
    }

    /**
     * Get list of available teams of a tournament
    */
    def getTeams(tournamentName: String): QueryEvent = {
        val aggMatch = Json.obj(
            ("$match", Json.obj( ("tournament_name", tournamentName) )))

        val setUnion = Json.obj( ("$setUnion", Json.arr("$home", "$away") ))
        val group = Json.obj(
            ("$group", Json.obj(
                ("_id", null),
                ("home", Json.obj( ("$addToSet", "$home_name") )),
                ("away", Json.obj( ("$addToSet", "$away_name") ))
            )))

        val project = Json.obj(
            ("$project", Json.obj(
                ("_id", 0),
                ("teams", setUnion)
            )))

        var cursor = Json.obj()

        var pipeline = Json.arr(aggMatch, group, project)
        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }

    def getAll(tournamentName: String, teamName: Option[String] = None): QueryEvent = {
        val filter = Json.obj(("tournament_name", tournamentName))
        val sort = Json.obj(("date", 1))

        if (teamName != None) {
            val nameQuery = Json.arr(Json.obj(("home_name", teamName.get)),
                                     Json.obj(("away_name", teamName.get)))
            filter.put("$or", nameQuery )
        }

        val query = new JsonObject().put("find", Collection)
            .put("filter", filter)
            .put("sort", sort)
            .put("batchSize", 250)

        QueryEvent("find", query)
    }


    def list(tournamentId: Option[String],
             tournamentName: Option[String],
             teamName: Option[String],
             sortBy: Option[String],
             window: Int): QueryEvent = {

        val maxDate = getDateByMillis(System.currentTimeMillis + (
            window * 86400000)) // 7 day window
        val minDate = getUTCdate()

        val dateFilter = Json.obj(("$gt", Json.obj(("$date", minDate))),
                                  ("$lt", Json.obj(("$date", maxDate))))

        val aggMatch = Json.obj(
            ("$match", Json.obj( ("date", dateFilter) )))

        if (tournamentId != None)
            // search by tournament id
            aggMatch.getJsonObject("$match").put("tournament_id", tournamentId.get)

        if (tournamentName != None)
            // search by tournament name
            aggMatch.getJsonObject("$match").put("tournament_name", tournamentName.get)

        if (teamName != None) {
            // search by team name
            val home = Json.obj(("home_name", teamName.get))
            val away = Json.obj(("away_name", teamName.get))

            aggMatch.getJsonObject("$match").put("$or", Json.arr(home, away))
        }
        println(teamName == None, teamName)
        val project_1 = Odds.projectDiff()
        var cursor = Json.obj()
        var pipeline = Json.arr(aggMatch, project_1)

        if (sortBy != None)
            pipeline.add(Json.obj(("$sort", Json.obj( (sortBy.get, 1) ))))

        if (tournamentId != None)
            pipeline.addAll(Json.arr(teamsToObjects, joinHomeTeam, joinAwayTeam))

        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }
}
