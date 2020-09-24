package fox.cub.router

import java.util.UUID.randomUUID

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.{EventBus, Message}
import io.vertx.lang.scala.ScalaLogger
import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject
import io.vertx.core.buffer.Buffer

import scala.util.{Failure, Success, Try}
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global
import scala.math

import fox.cub.utils.HttpUtils.{jsonResponse, errorResponse}
import fox.cub.db.DbProps
import fox.cub.model
import fox.cub.betting.BettingEvents
import fox.cub.http.validator.{
    HttpRequestValidator,
    RegexValidator,
    EnumValidator,
    MongoIdValidator}

import fox.cub.net.MLPNet
import fox.cub.internals.{QueryEvent, ResultEvent}

object StatisticalModel {
    val trainModelValidator = new HttpRequestValidator()
        .addQueryParam("type", new EnumValidator(model.TournamentModel.modelTypes))
        .addQueryParam("model_id", new MongoIdValidator)
        .addQueryParam("labels", new RegexValidator("^[0-9]+$"))
        .addQueryParam("inputs", new RegexValidator("^[0-9]+$"))
        .addQueryParam("epochs", new RegexValidator("^[0-9]+$"))
        .addQueryParam("batch",  new RegexValidator("^[0-9]+$"))

    /**
     * Using for testing only
    */
    def getGameStats(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentId = context.request.getParam("tournament_id")
        var json = context.getBodyAsJson.get

        var teamsScoring: Array[Float] = null

        try {
            teamsScoring = model.GameStats.getTeamsScoring(json, false)
            println(teamsScoring.mkString(" "))
        } catch {
            case err: Throwable => {
                logger.error(err.toString)
                errorResponse(context.response, err.toString, 500)
            }
        }

        val modelId = model.TournamentModel.getTournamentModel(tournamentId.get).get
        var totalDist = MLPNet.predict(teamsScoring,
                                       model.TournamentModel.getModel(modelId, "totals"))
        var scorelineDist = MLPNet.predict(teamsScoring,
                                           model.TournamentModel.getModel(modelId, "scoreline"))
        var bttsDist = MLPNet.predict(teamsScoring,
                                      model.TournamentModel.getModel(modelId, "btts"))

        var bEv = new BettingEvents(scorelineDist, totalDist, bttsDist)
        var statsJson = Json.obj(bEv.getEventsList: _*)

        logger.info(context.request.path.get)
        jsonResponse(response, statsJson)
    }

    def trainModel(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        val datasets = context.fileUploads()

        var numLabels = context.request.getParam("labels").get.toInt
        var numInputs = context.request.getParam("inputs").get.toInt
        var epochs = context.request.getParam("epochs").get.toInt
        var batchSize = context.request.getParam("batch").get.toInt
        var modelId = context.request.getParam("model_id").get
        var modelType = context.request.getParam("type").get

        val modelName = randomUUID.toString
        val errorMsg = "Invalid input"
        var uploadResult: JsonObject = null

        val onModelUploaded: Try[Message[ResultEvent]] => Unit = {
            case Success(result) => {
                model.TournamentModel.prepareModels(result.body.result)
                jsonResponse(response, uploadResult)
            }
            case Failure(err) => {
                logger.error(err.toString)
                errorResponse(context.response, err.toString, 500)
            }
        }

        if (datasets.size != 1) errorResponse(response, errorMsg, 500)
        else {
            val feature = Future[QueryEvent] {
                var file = datasets.head
                MLPNet.trainModel(file.uploadedFileName,
                                  modelName,
                                  numLabels,
                                  numInputs,
                                  epochs,
                                  batchSize)

                val binaryModel = MLPNet.getModel(modelName).toByteArray

                MLPNet.dropModel(modelName)
                model.TournamentModel.uploadModel(binaryModel,
                                                  modelType,
                                                  modelId)
            }

            feature
                .flatMap(query => eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)))
                .flatMap(result => {
                    uploadResult = result.body.result
                    eb.sendFuture[ResultEvent](DbProps.QueueName,
                                               Option(model.TournamentModel.getAllModels()))
                })
                .onComplete(onModelUploaded)
        }
    }
}
