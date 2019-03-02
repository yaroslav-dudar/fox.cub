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

    def getTournamentTable(results: JsonObject) = {
        val data  = results.getJsonArray("firstBatch")
        val teams = ListBuffer[JsonObject]()

        data.forEach(team => {
            var teamPoints = 0f
            val teamData = team.asInstanceOf[JsonObject]
            val teamId = teamData.getString("_id")

            teamData.getJsonArray("games").forEach(game => {
                val gameData = game.asInstanceOf[JsonObject]

                val goalsDiff = gameData.getInteger("goals_for") -
                    gameData.getInteger("goals_against")

                if (goalsDiff == 0) teamPoints += 1
                else if (goalsDiff > 0) teamPoints += 3
            })

            val teamRes = Json.obj(
                ("team_id", teamId),
                ("ppg", teamPoints / teamData.getJsonArray("games").size))

            teams.append(teamRes)
        })

        // sort teams by amount of points
        val sortedTeams = teams.sortBy(- _.getFloat("ppg"))
        Json.obj(("table", sortedTeams))
    }
}
