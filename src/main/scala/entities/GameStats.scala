package fox.cub.model

import scala.collection.JavaConverters._
import scala.collection.mutable.Buffer

import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.json.Json

import fox.cub.internals.QueryEvent
import fox.cub.math.helpers.{adjustedMean, expectedValue}
import fox.cub.utils.JsonUtils

object GameStats {
    private val Collection = "game_stats"

    def get(teamId: String): QueryEvent = {
        val filter = Json.obj(("team", teamId))
        val query = Json.obj(("find", Collection), ("filter", filter))
        QueryEvent("find", query)
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
            ("avgScoredHome", Json.obj(("$avg", "$goals_for"))),
            ("avgScoredAway", Json.obj(("$avg", "$goals_against")))
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
        teamOutput._2.put("scored", Json.obj(("$push", "$goals_for")))
        teamOutput._2.put("conceded", Json.obj(("$push", "$goals_against")))

        var homeMatch = Json.obj(("$match", Json.obj(
            ("tournament", touranmentId),
            ("venue", "home"),
            ("team", homeTeamId))))

        var homeTeam = Json.arr(
            homeMatch,
            Json.obj(("$bucket",  Json.obj(
                groupBy, boundaries, default, teamOutput
            )))
        )

        var awayMatch = Json.obj(("$match", Json.obj(
            ("tournament", touranmentId),
            ("venue", "away"),
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

    def getTeamsStrength(json: JsonObject) = {
        val stats = json.getJsonArray("firstBatch").getJsonObject(0)
        val touranmentStats = stats.getJsonArray("tournament_avg").getJsonObject(0)
        val homeStats = stats.getJsonArray("home_team").getJsonObject(0)
        val awayStats = stats.getJsonArray("away_team").getJsonObject(0)

        var homeScoredMean = adjustedMean(JsonUtils.arrayToBuffer(homeStats.getJsonArray("scored")))
        var awayScoredMean = adjustedMean(JsonUtils.arrayToBuffer(awayStats.getJsonArray("scored")))

        var homeConcededMean = adjustedMean(JsonUtils.arrayToBuffer(homeStats.getJsonArray("conceded")))
        var awayConcededMean = adjustedMean(JsonUtils.arrayToBuffer(awayStats.getJsonArray("conceded")))

        var homeAttack = homeScoredMean / touranmentStats.getFloat("avgScoredHome")
        var homeDefend = homeConcededMean / touranmentStats.getFloat("avgScoredAway")
        // avgScoredAway - away team scored avg, avgScoredHome - away team conceded
        var awayAttack = awayScoredMean / touranmentStats.getFloat("avgScoredAway")
        var awayDefend = awayConcededMean / touranmentStats.getFloat("avgScoredHome")

        var homeStrength = homeAttack * touranmentStats.getFloat("avgScoredHome") * awayDefend
        var awayStrangth = awayAttack * touranmentStats.getFloat("avgScoredAway") * homeDefend
        println((homeStrength, awayStrangth))
        (homeStrength, awayStrangth)
    }
}
