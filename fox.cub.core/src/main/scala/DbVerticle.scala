package fox.cub.db

import io.vertx.lang.scala.{ScalaVerticle, ScalaLogger}
import io.vertx.scala.config.{ConfigStoreOptions, ConfigRetriever}
import io.vertx.scala.core.eventbus.{MessageConsumer, Message}
import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import io.vertx.scala.ext.mongo.MongoClient
import com.mongodb.MongoCommandException

import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

import scala.util.{Failure, Success, Try}

import fox.cub.internals.{QueryEvent, ResultEvent}
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
    private var consumer:  MessageConsumer[QueryEvent] = null

    override def startFuture(): Future[Unit] = {
        var retriever = ConfigRetriever.create(vertx)
        consumer = vertx.eventBus.consumer[QueryEvent](DbProps.QueueName)

        retriever.getConfigFuture.flatMap(config => {
            client = MongoClient.createShared(
                vertx,
                config.getJsonObject(DbSettings),
                "REST_API_POOL")

            consumer.completionFuture().onComplete(onConsumerStarted)
            registerQueryHandler.completionFuture
        })
    }

    override def stopFuture(): Future[Unit] =  {
        Future { client.close }
    }

    def replyResult(result: JsonObject, msg: Message[QueryEvent]) {
        val cursor = result.getJsonObject("cursor")
        val ok = result.getDouble("ok")
        val writeErr = result.getJsonArray("writeErrors")

        if (cursor != null) msg.reply(ResultEvent(cursor))
        else if (writeErr != null) msg.fail(422, writeErr.toString)
        else if (ok == 1) msg.reply(ResultEvent(result))
        else msg.reply(ResultEvent(result))
    }

    /**
     * Registering Vertx Query handler
     */
    def registerQueryHandler(): MessageConsumer[QueryEvent] = {
        consumer.handler(msg => {
            val onRegistered: Try[JsonObject] => Unit = {
                case Success(result: JsonObject) => {
                    replyResult(result, msg)
                }
                case Failure(cause: MongoCommandException) => {
                    logger.error(cause.getStackTraceString)
                    msg.fail(422, cause.toString)
                }
                case Failure(cause) => {
                    logger.error(cause.getStackTraceString)
                    msg.fail(422, cause.toString)
                }
            }

            client
                .runCommandFuture(
                    msg.body.command,
                    msg.body.query)
                .onComplete(onRegistered)
        })
    }

    val onConsumerStarted: Try[Unit] => Unit = {
        case Success(_) => {
            val modelQuery = model.TournamentModel.getAllModels()
            val tournamentQuery = model.Tournament.getAll()

            vertx.eventBus()
                .sendFuture[ResultEvent](DbProps.QueueName, modelQuery)
                .onComplete {
                    case Success(result) => {
                        model.TournamentModel.prepareModels(result.body.result)
                    }
                    case Failure(cause) => logger.error(s"$cause")
            }

            vertx.eventBus()
                .sendFuture[ResultEvent](DbProps.QueueName, tournamentQuery)
                .onComplete {
                    case Success(result) => {
                        model.TournamentModel.prepareTournaments(result.body.result)
                    }
                    case Failure(cause) => logger.error(s"$cause");
            }
        }
        case Failure(cause: Throwable) => logger.error(s"$cause");
    }
}
