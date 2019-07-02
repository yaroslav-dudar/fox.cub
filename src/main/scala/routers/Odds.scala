package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.http.validator.{HttpRequestValidator, RegexValidator}
import fox.cub.utils.HttpUtils.jsonResponse
import fox.cub.db.DbProps
import fox.cub.model

object Odds {

    val getOddsValidator = new HttpRequestValidator()
        .addQueryParam("fixture_id", new RegexValidator("^[0-9]+$"))

    def getOdds(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var fixtureId = context.request.getParam("fixture_id")
        var query = model.Odds.get(fixtureId.get.toInt)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.getStackTraceString)
                context.fail(500)
            }
        }
    }
}
