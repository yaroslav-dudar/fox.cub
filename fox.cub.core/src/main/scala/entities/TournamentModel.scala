package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.ext.web.FileUpload
import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.ScalaLogger

import fox.cub.internals.QueryEvent
import fox.cub.net.MLPNet
import fox.cub.model

import java.util.Base64

object TournamentModel {
    private val Collection = "tournament_model"
    private val logger = ScalaLogger.getLogger(this.getClass.getName)
    val modelTypes = List("btts", "totals", "scoreline",
                          "bttsLive", "totalsLive", "scorelineLive")

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
     * Parse model binary data and load it to the application memory
    */
    def setupModel(modelJson: JsonObject) {
        val modelId = modelJson.getJsonObject("_id").getString("$oid")

        modelTypes.foreach(_type => {
            if (!modelJson.containsKey(_type)) return;
            val model = modelJson.getJsonObject(_type).getString("$binary")
            MLPNet.loadModel(getModel(modelId, _type),
                             Base64.getDecoder().decode(model))
        })
    }

    /**
     * Update selected model type with new model binary file
    */
    def uploadModel(modelContent: Array[Byte], modelType: String, modelId: String) = {
        val q = Json.obj(("_id", Json.obj(("$oid", modelId))))
        val binaryData = new JsonObject().put("$binary", modelContent)
        val u = Json.obj(("$set", Json.obj((modelType, binaryData))))
        val update = Json.obj(("q", q), ("u", u), ("upsert", false))
        val query = new JsonObject().put("update", Collection)
            .put("updates", Json.arr(update))
        QueryEvent("update", query)
    }

    def getModel(modelId: String, modelType: String) = s"$modelId.$modelType"

    /**
     * Upload statistical model from DB to app memory
    */
    def prepareModels(result: JsonObject) {
        result.getJsonArray("firstBatch").forEach(statsModel => {
            statsModel match {
                case m: JsonObject => {
                    model.TournamentModel.setupModel(m)
                }
                case m => { logger.warn(
                    s"""Model: $m not loaded to application.
                    Has incorrect format""") }
            }
        })
    }

    /**
     * Generate mapping from tournament to the statistical model
    */
    def prepareTournaments(result: JsonObject) {
        result.getJsonArray("firstBatch").forEach(tournament => {
            tournament match {
                case t: JsonObject => {
                    model.TournamentModel.addTournament(
                        model.Tournament.getId(t),
                        model.Tournament.getModel(t))
                }
                case t => { logger.warn(
                    s"""Tournament: $t not loaded to application.
                    Has incorrect format""") }
            }
        })
    }
}
