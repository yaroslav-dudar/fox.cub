package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.{jsonResponse, errorResponse}
import fox.cub.db.DbProps
import fox.cub.model

object Market {

    def getTeams(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentName = context.request.getParam("tournament")
        var query = model.Fixtures.getTeams(tournamentName.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.getStackTraceString)
                errorResponse(context.response, cause.toString, 500)
            }
        }
    }

    def getFixtures(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentName = context.request.getParam("tournament")
        var teamName = context.request.getParam("team")
        var query = model.Fixtures.getAll(tournamentName.get, teamName)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.getStackTraceString)
                errorResponse(context.response, cause.toString, 500)
            }
        }
    }

    def getTournaments(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var query = model.Fixtures.getTournaments()

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.getStackTraceString)
                errorResponse(context.response, cause.toString, 500)
            }
        }
    }
}
