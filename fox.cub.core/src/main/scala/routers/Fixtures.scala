package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.{jsonResponse, errorResponse}
import fox.cub.http.validator.{HttpRequestValidator,
                               MongoIdValidator,
                               RegexValidator}
import fox.cub.db.DbProps
import fox.cub.model

object Fixtures {

    val dateReg = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"

    val fixturesListValidator = new HttpRequestValidator()
        .addQueryParam("end", new RegexValidator(dateReg))
        .addQueryParam("start", new RegexValidator(dateReg))

    val addFavFixtuteValidator = new HttpRequestValidator()
        .addJsonBodyParam("fixture_id", new MongoIdValidator, classOf[java.lang.String])

    def list(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentId = context.request.getParam("tournament_id")
        var tournamentName = context.request.getParam("tournament_name")
        var teamName = context.request.getParam("team_name")
        var sortBy = context.request.getParam("sort_by")
        var start = context.request.getParam("start").get
        var end = context.request.getParam("end").get

        var query = model.Fixtures.list(tournamentId,
                                        tournamentName,
                                        teamName,
                                        sortBy,
                                        start,
                                        end)

        eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
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
