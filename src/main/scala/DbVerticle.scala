package fox.cub.db

import io.vertx.lang.scala.ScalaVerticle
import io.vertx.scala.ext.mongo.MongoClient
import io.vertx.scala.config.{ConfigStoreOptions, ConfigRetriever}
import io.vertx.scala.core.eventbus.{MessageConsumer, Message}
import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import scala.concurrent.Future
import scala.util.{Failure, Success}
import scala.collection.mutable.Buffer

import fox.cub.internals.{QueryEvent, ResultEvent}

/**
 * Module to interact with DB. Contain db connection pool
*/
class DatabaseVerticle extends ScalaVerticle {
    private val DbSettings = "database"
    private val QueueName = "db.queue"
    private var client: MongoClient = null

    override def startFuture(): Future[Unit] = {
        var retriever = ConfigRetriever.create(vertx)
        var consumer = vertx.eventBus.consumer[QueryEvent](QueueName)

        retriever.getConfigFuture.flatMap(config => {
            client = MongoClient.createShared(
                vertx,
                config.getJsonObject(DbSettings),
                "REST_API_POOL")

            consumer.handler(msg => {
                client.runCommandFuture(msg.body.command, msg.body.query).onComplete{
                    case Success(result: JsonObject) => {
                        msg.reply(ResultEvent(result))
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
}
