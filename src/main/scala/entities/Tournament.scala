package fox.cub.model

import scala.collection.mutable.ListBuffer

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent

object Tournament {
    private val Collection = "tournament"

    def getAll(): QueryEvent = {
        val query = new JsonObject().put("find", Collection)
        QueryEvent("find", query)
    }

    def getModel(result: JsonObject) = {
        result.getString("tournament_model")
    }

    def getId(result: JsonObject) = {
        result.getJsonObject("_id").getString("$oid")
    }

    /**
     * Calculate tournament standings
    */
    def getTournamentTable(results: JsonObject) = {
        val data  = results.getJsonArray("firstBatch")
        val teams = ListBuffer[JsonObject]()

        data.forEach(team => {
            var teamPoints = 0f
            var teamScored = 0f
            var teamConceded = 0f
            val teamData = team.asInstanceOf[JsonObject]
            val teamId = teamData.getString("_id")

            teamData.getJsonArray("games").forEach(game => {
                val gameData = game.asInstanceOf[JsonObject]

                val goalsDiff = gameData.getInteger("goals_for") -
                    gameData.getInteger("goals_against")

                if (goalsDiff == 0) teamPoints += 1
                else if (goalsDiff > 0) teamPoints += 3

                teamScored += gameData.getInteger("goals_for")
                teamConceded += gameData.getInteger("goals_against")
            })

            val games_count = teamData.getJsonArray("games").size
            val teamRes = Json.obj(
                ("team_id", teamId),
                ("ppg", teamPoints / games_count),
                ("spg", teamScored / games_count),
                ("cpg", teamConceded / games_count))

            teams.append(teamRes)
        })

        // sort teams by points
        val sortedTeams = teams.sortBy(- _.getFloat("ppg"))
        Json.obj(("table", sortedTeams))
    }
}
