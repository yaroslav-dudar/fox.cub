package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.http.validator.{HttpRequestValidator, MongoIdValidator}
import fox.cub.utils.HttpUtils.jsonResponse
import fox.cub.db.DbProps
import fox.cub.model

object GameOdds {

    val getOddsValidator = new HttpRequestValidator()
        .addQueryParam("tournament_id", new MongoIdValidator)

    /**
     * Return not exipired odds in a given tournament
    */
    def getOdds(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentId = context.request.getParam("tournament_id")
        var query = model.GameOdds.getRecent(tournamentId.get)

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