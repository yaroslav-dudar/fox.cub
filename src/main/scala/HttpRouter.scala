package fox.cub.http

import io.vertx.scala.ext.web.{Router, RoutingContext}
import io.vertx.scala.ext.mongo.MongoClient
import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.ScalaLogger
import io.vertx.lang.scala.json.Json
import io.vertx.scala.core.Vertx
import io.vertx.scala.core.eventbus.Message
import io.vertx.core.eventbus.{EventBus, ReplyException}

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.{QueryEvent, QueryEventCodec}
import fox.cub.internals.{ResultEvent, ResultEventCodec}

import fox.cub.model.{GameStats, Team}
/**
 * Web routers, handlers
*/
class HttpRouter(vertx: Vertx, config: JsonObject) {
    private val DbQueueName = "db.queue"
    // init logger
    private val logger = ScalaLogger.getLogger(this.getClass.getName)
    private val _router = Router.router(vertx)

    private val eb = vertx.eventBus()

    // register custom message codecs
    eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
        classOf[QueryEvent], new QueryEventCodec())
    eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
        classOf[ResultEvent], new ResultEventCodec())

    router.get("/api/v1/game/:id").handler(getGame)
    router.get("/api/v1/team/:name").handler(getTeam)

    def router = _router

    def getGame(context: RoutingContext) {
        var response = context.response
        var id = context.request.getParam("id")
        var query = GameStats.get(id.get)

        val data = eb.sendFuture[ResultEvent](DbQueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result.encode

                logger.info(context.request.path.get)
                response.putHeader("content-type", "application/json")
                response.setChunked(true)
                response.write(json).end()
            }
            case Failure(cause: ReplyException) => {
                logger.error(cause.toString)
                context.fail(cause.failureCode)
            }
        }
    }

    def getTeam(context: RoutingContext) {
        var response = context.response
        var name = context.request.getParam("name")
        var query = Team.get(name.get)

        val data = eb.sendFuture[ResultEvent](DbQueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result.encode

                logger.info(context.request.path.get)
                response.putHeader("content-type", "application/json")
                response.setChunked(true)
                response.write(json).end()
            }
            case Failure(cause: ReplyException) => {
                logger.error(cause.toString)
                context.fail(cause.failureCode)
            }
        }
    }
}
