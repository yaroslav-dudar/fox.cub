package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.{jsonResponse, errorResponse}
import fox.cub.http.validator.{HttpRequestValidator,
                               RegexValidator}
import fox.cub.db.DbProps
import fox.cub.model

object Fixtures {

    val fixturesListValidator = new HttpRequestValidator()
        .addQueryParam("window", new RegexValidator("^[0-9]+$"))

    def getUpcomingFixtures(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentId = context.request.getParam("tournament_id")
        var query = model.Fixtures.getRecent(tournamentId)

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

    def list(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentId = context.request.getParam("tournament_id")
        var tournamentName = context.request.getParam("tournament_name")
        var teamName = context.request.getParam("team_name")
        var sortBy = context.request.getParam("sort_by")
        var window = context.request.getParam("window").get.toInt

        var query = model.Fixtures.list(tournamentId,
                                        tournamentName,
                                        teamName,
                                        sortBy,
                                        window)

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
