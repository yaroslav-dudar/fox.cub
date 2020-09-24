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

object Team {

    /**
     * Return team results in a tournament
    */
    def getGames(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var team = context.request.getParam("team_id")
        var tournament = context.request.getParam("tournament_id")
        var query = model.GameStats.get(team.get, tournament)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                errorResponse(context.response, cause.toString, 500)
            }
        }
    }

    def getTeam(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var team = context.request.getParam("team_id")
        var query = model.Team.get(team.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                errorResponse(context.response, cause.toString, 500)
            }
        }
    }

    def getTeamNotes(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var team = context.request.getParam("team_id")
        var user = context.request.getParam("user_id")
        var query = model.Team.get(team.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                errorResponse(context.response, cause.toString, 500)
            }
        }
    }
}