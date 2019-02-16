package fox.cub.model

import scala.collection.JavaConverters._
import scala.collection.mutable.Buffer

import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.json.Json

import fox.cub.internals.QueryEvent
import fox.cub.math.helpers.{adjustedMean, expectedValue}
import fox.cub.utils.JsonUtils
import fox.cub.math.CMP

object GameStats {
    private val Collection = "game_stats"

    /**
     * Get team performed games with opponents detailed info
    */
    def get(teamId: String, tournamentId: String): QueryEvent = {
        val aggMatch = Json.obj(
            ("$match", Json.obj(
                ("team", teamId), ("tournament", tournamentId))
            ))

        val teamsToObjects =  Json.obj(("$addFields", Json.obj(
                ("team", Json.obj(("$toObjectId", "$team"))),
                ("opponent", Json.obj(("$toObjectId", "$opponent")))
            )))

        val joinTeam = Json.obj(("$lookup", Json.obj(
            ("from", "team"),
            ("localField", "team"),
            ("foreignField", "_id"),
            ("as", "team")
            )))

        val joinOpponent = Json.obj(("$lookup", Json.obj(
            ("from", "team"),
            ("localField", "opponent"),
            ("foreignField", "_id"),
            ("as", "opponent")
            )))

        var pipeline = Json.arr(aggMatch, teamsToObjects, joinTeam, joinOpponent)
        // cursor with the default batch size
        var cursor = Json.obj()
        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }

    /**
     * Get both teams avg offensive and defensive strength
     * Get touranment avg offensive and defensive strength
     *
     * @param venue should be away or home
    */
    def getTeamsStrength(touranmentId: String, awayTeamId: String, homeTeamId: String)
        :QueryEvent = {

        var groupBy = ("groupBy", "$_id")
        var boundaries = ("boundaries", Json.arr(0, 150))
        var default = ("default", "Other")
        var overallOutput = ("output", Json.obj(
            ("avgScoredHome", Json.obj(("$avg", "$xG_for"))),
            ("avgScoredAway", Json.obj(("$avg", "$xG_against")))
        ))
        var overallMatch = Json.obj(("$match", Json.obj(("tournament", touranmentId), ("venue", "home"))))

        var avgTournament = Json.arr(
            overallMatch,
            Json.obj(("$bucket",  Json.obj(
                groupBy, boundaries, default, overallOutput
            )))
        )

        // list of of scored and conceded goals by a team
        var teamOutput = (overallOutput._1, overallOutput._2)
        teamOutput._2.put("scored_xg", Json.obj(("$push", "$xG_for")))
        teamOutput._2.put("conceded_xg", Json.obj(("$push", "$xG_against")))
        teamOutput._2.put("scored", Json.obj(("$push", "$goals_for")))
        teamOutput._2.put("conceded", Json.obj(("$push", "$goals_against")))

        var homeMatch = Json.obj(("$match", Json.obj(
            ("tournament", touranmentId),
            //("venue", "home"),
            ("team", homeTeamId))))

        var homeTeam = Json.arr(
            homeMatch,
            Json.obj(("$bucket",  Json.obj(
                groupBy, boundaries, default, teamOutput
            )))
        )

        var awayMatch = Json.obj(("$match", Json.obj(
            ("tournament", touranmentId),
            //("venue", "away"),
            ("team", awayTeamId))))

        var awayTeam = Json.arr(
            awayMatch,
            Json.obj(("$bucket",  Json.obj(
                groupBy, boundaries, default, teamOutput
            )))
        )

        var facet = Json.obj(("$facet", Json.obj(
            ("tournament_avg", avgTournament),
            ("home_team", homeTeam),
            ("away_team", awayTeam)
        )))

        var pipeline = Json.arr(facet)
        // cursor with the default batch size
        var cursor = Json.obj()

        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }

    /**
     * Get metrics for goals mlp model
     * @param considerActualGoals
     *  true - use also actual goals scored and conceded
     *  false - use only expected goals
    */
    def getTeamsScoring(json: JsonObject, considerActualGoals: Boolean = true) = {
        val stats = json.getJsonArray("firstBatch").getJsonObject(0)
        var touranmentStats = _getTournamentStats(stats)

        var homeScored = 0.0f
        var awayScored = 0.0f
        var homeConceded = 0.0f
        var awayConceded = 0.0f

        val homeStats = stats.getJsonArray("home_team").getJsonObject(0)
        val awayStats = stats.getJsonArray("away_team").getJsonObject(0)

        var homeScoredXG: Buffer[Double] = JsonUtils.arrayToBuffer(homeStats.getJsonArray("scored_xg"))
        var awayScoredXG: Buffer[Double] = JsonUtils.arrayToBuffer(awayStats.getJsonArray("scored_xg"))
        var homeConcededXG: Buffer[Double] = JsonUtils.arrayToBuffer(homeStats.getJsonArray("conceded_xg"))
        var awayConcededXG: Buffer[Double] = JsonUtils.arrayToBuffer(awayStats.getJsonArray("conceded_xg"))

        homeScored = expectedValue(homeScoredXG)
        awayScored = expectedValue(awayScoredXG)
        homeConceded = expectedValue(homeConcededXG)
        awayConceded = expectedValue(awayConcededXG)

        if (considerActualGoals) {
            var homeScoredActual: Buffer[Int] = JsonUtils.arrayToBuffer(homeStats.getJsonArray("scored"))
            var awayScoredActual: Buffer[Int] = JsonUtils.arrayToBuffer(awayStats.getJsonArray("scored"))
            var homeConcededActual: Buffer[Int] = JsonUtils.arrayToBuffer(homeStats.getJsonArray("conceded"))
            var awayConcededActual: Buffer[Int] = JsonUtils.arrayToBuffer(awayStats.getJsonArray("conceded"))

            homeScored = (homeScored + expectedValue(homeScoredActual)) / 2
            awayScored = (awayScored + expectedValue(awayScoredActual)) / 2
            homeConceded = (homeConceded + expectedValue(homeConcededActual)) / 2
            awayConceded = (awayConceded + expectedValue(awayConcededActual)) / 2
        }

        Array(
            getAvgTournamentTotal(stats),
            homeScored,
            homeConceded,
            awayScored,
            awayConceded)
    }

    /**
     * Fetch average goals scored in tournament
     * @param vanueFiltered if true result filtered by vanue
     *  else return avg scores in tournament
    */
    def _getTournamentStats(stats: JsonObject, vanueFiltered: Boolean = false): JsonObject = {
        var touranmentStats = stats.getJsonArray("tournament_avg").getJsonObject(0)

        if (!vanueFiltered) {
            val tournamentAvg = (touranmentStats.getFloat("avgScoredAway") +
                touranmentStats.getFloat("avgScoredHome")) / 2
            touranmentStats = Json.obj(
                ("avgScoredHome", tournamentAvg),
                ("avgScoredAway", tournamentAvg)
            )
        }

        touranmentStats
    }

    /**
     * Get average amount of goals per game
    */
    def getAvgTournamentTotal(stats: JsonObject) = {
        var touranmentStats = stats.getJsonArray("tournament_avg").getJsonObject(0)
        touranmentStats.getFloat("avgScoredAway") + touranmentStats.getFloat("avgScoredHome")
    }
}
