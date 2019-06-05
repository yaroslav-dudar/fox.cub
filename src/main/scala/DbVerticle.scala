package fox.cub.db

import io.vertx.lang.scala.{ScalaVerticle, ScalaLogger}
import io.vertx.scala.ext.mongo.MongoClient
import io.vertx.scala.config.{ConfigStoreOptions, ConfigRetriever}
import io.vertx.scala.core.eventbus.{MessageConsumer, Message}
import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import scala.concurrent.Future
import scala.util.{Failure, Success}
import scala.collection.mutable.Buffer

import fox.cub.internals.{QueryEvent, ResultEvent}

import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.jsonResponse
import fox.cub.model

object DbProps {
    val QueueName = "db.queue"
}

/**
 * Module to interact with DB. Contain db connection pool
*/
class DatabaseVerticle extends ScalaVerticle {

    val DbSettings = "database"
    private var client: MongoClient = null

    private val logger = ScalaLogger.getLogger(this.getClass.getName)

    override def startFuture(): Future[Unit] = {
        var retriever = ConfigRetriever.create(vertx)
        var consumer = vertx.eventBus.consumer[QueryEvent](DbProps.QueueName)

        retriever.getConfigFuture.flatMap(config => {
            client = MongoClient.createShared(
                vertx,
                config.getJsonObject(DbSettings),
                "REST_API_POOL")

            consumer.completionFuture().onComplete{
                case Success(result) => {
                    val modelQuery = model.TournamentModel.getAllModels()
                    val tournamentQuery = model.Tournament.getAll()

                    vertx.eventBus().sendFuture[ResultEvent](DbProps.QueueName, modelQuery).onComplete {
                        case Success(result) => {
                            prepareModels(result.body.result)
                        }
                        case Failure(cause) => logger.error(s"$cause")
                    }

                    vertx.eventBus().sendFuture[ResultEvent](DbProps.QueueName, tournamentQuery).onComplete {
                        case Success(result) => {
                            prepareTournaments(result.body.result)
                        }
                        case Failure(cause) => logger.error(s"$cause")
                    }
                }
                case Failure(cause) => logger.error(s"$cause")
            }

            consumer.handler(msg => {
                client.runCommandFuture(msg.body.command, msg.body.query).onComplete{
                    case Success(result: JsonObject) => {
                        msg.body.command match {
                            case "find" | "aggregate" | "insert" => _processResult(result, msg)
                            case _ => _processResult(result, msg)
                        }
                    }
                    case Failure(cause: com.mongodb.MongoCommandException) => {
                        msg.fail(422, cause.toString)
                    }
                    case Failure(cause) => {
                        msg.fail(422, cause.toString)
                    }
                }
            }).completionFuture
        })
    }

    override def stopFuture(): Future[Unit] =  {
        Future { client.close }
    }

    def _processResult(result: JsonObject, msg: Message[QueryEvent]) {
        val cursor = result.getJsonObject("cursor")
        val ok = result.getDouble("ok")
        val writeErr = result.getJsonArray("writeErrors")

        if (cursor != null) msg.reply(ResultEvent(cursor))
        else if (writeErr != null) msg.fail(422, writeErr.toString)
        else if (ok == 1) msg.reply(ResultEvent(result))
        else msg.reply(ResultEvent(result))
    }

    /**
     * Upload statistical model from DB to app memory
    */
    def prepareModels(result: JsonObject) {
        result.getJsonArray("firstBatch").forEach(m => {
            val modelData = m.asInstanceOf[JsonObject]
            model.TournamentModel.setupModel(modelData)
        })
    }

    /**
     * Generate mapping from tournament to the statistical model
    */
    def prepareTournaments(result: JsonObject) {
        result.getJsonArray("firstBatch").forEach(t => {
            val tournament = t.asInstanceOf[JsonObject]
            val modelId = model.Tournament.getModel(tournament)
            val tournamentId = model.Tournament.getId(tournament)

            model.TournamentModel.addTournament(tournamentId, modelId)
        })
    }
}
