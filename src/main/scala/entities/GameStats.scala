package fox.cub.model

import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.json.Json

import fox.cub.internals.QueryEvent

object GameStats {
    private val Collection = "game_stats"

    def get(id: String): QueryEvent = {
        val query = new JsonObject().put("find", Collection).put("_id", id)
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

        // list of of scored goals by a team
        var teamOutput = (overallOutput._1, overallOutput._2)
        teamOutput._2.put("scored", Json.obj(("$push", "$goals_for")))

        var homeMatch = Json.obj(("$match", Json.obj(
            ("tournament", touranmentId),
            //("venue", "home"),
            ("team", homeTeamId))))

        var avgHomeTeam = Json.arr(
            homeMatch,
            Json.obj(("$bucket",  Json.obj(
                groupBy, boundaries, default, teamOutput
            )))
        )

        var awayMatch = Json.obj(("$match", Json.obj(
            ("tournament", touranmentId),
            //("venue", "away"),
            ("team", awayTeamId))))

        var avgAwayTeam = Json.arr(
            awayMatch,
            Json.obj(("$bucket",  Json.obj(
                groupBy, boundaries, default, teamOutput
            )))
        )

        var facet = Json.obj(("$facet", Json.obj(
            ("tournament_avg", avgTournament),
            ("home_team_avg", avgHomeTeam),
            ("away_team_avg", avgAwayTeam)
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
        println(stats)
        val touranmentStats = stats.getJsonArray("tournament_avg").getJsonObject(0)
        val homeStats = stats.getJsonArray("home_team_avg").getJsonObject(0)
        val awayStats = stats.getJsonArray("away_team_avg").getJsonObject(0)

        var homeAttack = homeStats.getFloat("avgScoredHome") / touranmentStats.getFloat("avgScoredHome")
        var homeDefend = homeStats.getFloat("avgScoredAway") / touranmentStats.getFloat("avgScoredAway")

        var awayAttack = awayStats.getFloat("avgScoredHome") / touranmentStats.getFloat("avgScoredHome")
        var awayDefend = awayStats.getFloat("avgScoredAway") / touranmentStats.getFloat("avgScoredAway")

        var homeStrength = homeAttack * touranmentStats.getFloat("avgScoredHome") * awayDefend
        var awayStrangth = awayAttack * touranmentStats.getFloat("avgScoredAway") * homeDefend

        (homeStrength, awayStrangth)
    }
}
