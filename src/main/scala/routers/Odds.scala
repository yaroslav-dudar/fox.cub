package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.http.validator.{HttpRequestValidator, RegexValidator}
import fox.cub.utils.HttpUtils.{jsonResponse, errorResponse}
import fox.cub.db.DbProps
import fox.cub.model

object Odds {

    val getOddsValidator = new HttpRequestValidator()
        .addQueryParam("fixture_id", new RegexValidator("^[0-9]+$"))

    def getOdds(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        // fetching input list of fixture ids
        var fixtureIds = context.request
            .params()
            .getAll("fixture_id")
            .map(f => f.toInt)

        var query = model.Odds.get(fixtureIds)

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

    /**
     * Calculate difference between open and closing lines
     */
    def getDiff(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        // fetching input list of fixture ids
        var fixtureIds = context.request
            .params()
            .getAll("fixture_id")
            .map(f => f.toInt)

        var query = model.Odds.getDiff(fixtureIds)

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
