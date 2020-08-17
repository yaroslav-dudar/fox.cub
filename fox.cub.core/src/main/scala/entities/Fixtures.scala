package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.{JsonObject, JsonArray}

import fox.cub.internals.QueryEvent
import fox.cub.utils.Utils.{getUTCdate, getDateByMillis, getTimeMillisByStr}

import scala.collection.mutable.{ListBuffer, Map}
import scala.collection.immutable.ListMap
import scala.math.{abs}

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

    /**
     * Get list of fixtures within given time window
     * @param tournamentId Fixtures belongs to a tournament id
       @param teamName Fixtures belongs with a given team
       @param sortBy Fixtures sort by field
       @param tournamentName Fixtures belongs to a tournament name
       @param start min timestmap of output Fixtures
       @param end max timestmap of output Fixtures
    */
    def list(tournamentId: Option[String],
             tournamentName: Option[String],
             teamName: Option[String],
             sortBy: Option[String],
             start: String,
             end: String,
             liteOutput: Boolean = false): QueryEvent = {

        val maxDate = getDateByMillis(getTimeMillisByStr(end))
        val minDate = getDateByMillis(getTimeMillisByStr(start))

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

        val project_1 = Odds.projectDiff(liteOutput)
        var cursor = Json.obj(("batchSize", 250))
        var pipeline = Json.arr(aggMatch, project_1)

        if (sortBy != None)
            pipeline.add(Json.obj(("$sort", Json.obj( (sortBy.get, 1) ))))

        if (tournamentId != None)
            pipeline.addAll(Json.arr(teamsToObjects, joinHomeTeam, joinAwayTeam))

        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }

    def groupByTeam(fixturesList: JsonArray) = {
        var groups = Json.obj()
        //fixturesList.get

        var teamDiffs = Map[String, ListBuffer[Float]]()
        var finalDiffs = Map[String, Float]()

        fixturesList.forEach(f => {
            val fixture = f.asInstanceOf[JsonObject]
            val teamHome = fixture.getString("home_name")
            val teamAway = fixture.getString("away_name")
            var diff = abs(1 - fixture.getFloat("homeDiff"))
            if (diff == 1.0) diff = 0f

            if (teamDiffs.get(teamHome) == None)
                teamDiffs += (teamHome -> ListBuffer[Float]())
            if (teamDiffs.get(teamAway) == None)
                teamDiffs += (teamAway -> ListBuffer[Float]())

            teamDiffs(teamHome) += diff
            teamDiffs(teamAway) += diff
        })

        teamDiffs.foreach{ case (k,v) => finalDiffs += (k -> v.sum / v.length ) }
        teamDiffs.clear

        var sortedResults = new JsonObject();

        ListMap(finalDiffs.toSeq.sortWith(_._2 > _._2):_*)
            .foreach(v => sortedResults.put(v._1, v._2))
        sortedResults
    }

    def listByIds(ids: JsonArray) = {
        val filter = Json.obj(("_id", Json.obj(("$in", ids))))
        val query = new JsonObject().put("find", Collection).put("filter", filter)
        QueryEvent("find", query)
    }
}
