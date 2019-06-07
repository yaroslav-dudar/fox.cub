package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent
import fox.cub.net.MLPNet

import java.util.Base64

object TournamentModel {
    private val Collection = "tournament_model"

    // collection of tournament id and appropriate model id
    var tournamentModels = scala.collection.mutable.Map[String, String]()

    def getAllModels(): QueryEvent = {
        val query = Json.obj(("find", Collection))
        QueryEvent("find", query)
    }

    def addTournament(tournamentId: String, modelId: String) {
        tournamentModels += (tournamentId -> modelId)
    }

    def getTournamentModel(tournamentId: String): Option[String] = {
        tournamentModels.get(tournamentId)
    }

    /**
     * Parse model bytes and load it to the application memory
    */
    def setupModel(modelJson: JsonObject) {
        val modelId = modelJson.getJsonObject("_id").getString("$oid")
        val bttsModel = modelJson.getJsonObject("btts").getString("$binary")
        val totalModel = modelJson.getJsonObject("totals").getString("$binary")
        val scorelineModel = modelJson.getJsonObject("scoreline").getString("$binary")

        MLPNet.loadModel(getBttsModel(modelId), Base64.getDecoder().decode(bttsModel))
        MLPNet.loadModel(getTotalsModel(modelId), Base64.getDecoder().decode(totalModel))
        MLPNet.loadModel(getScorelineModel(modelId), Base64.getDecoder().decode(scorelineModel))
    }

    def getBttsModel(modelId: String) = modelId + ".btts"

    def getScorelineModel(modelId: String) = modelId + ".scoreline"

    def getTotalsModel(modelId: String) = modelId + ".totals"
}
