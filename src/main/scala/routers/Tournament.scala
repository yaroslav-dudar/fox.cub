package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.jsonResponse
import fox.cub.db.DbProps
import fox.cub.model

object Tournament {

    /**
     * Return list of teams participating in tournament
    */
    def getTournamentTeams(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournament = context.request.getParam("tournament_id")
        var query = model.Team.getByTournament(tournament.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                context.fail(500)
            }
        }
    }

    /**
     * Return list of available tournaments in a system
    */
    def getTournamentsList(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var query = model.Tournament.getAll()

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                context.fail(500)
            }
        }
    }

    def getTournamentTable(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournament = context.request.getParam("tournament_id")
        var query = model.GameStats.getTeamResults(tournament.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                val table = model.Tournament.getTournamentTable(json)
                logger.info(context.request.path.get)
                jsonResponse(response, table)
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                context.fail(500)
            }
        }
    }
}