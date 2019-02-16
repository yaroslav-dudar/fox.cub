package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger
import io.vertx.lang.scala.json.Json

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.jsonResponse
import fox.cub.db.DbProps
import fox.cub.model
import fox.cub.math.CMP
import fox.cub.betting.BettingEvents
import fox.cub.http.validator.{HttpRequestValidator, MongoIdValidator}
import fox.cub.net.MLPNet

object GameStats {

    val getGameStatsValidator = new HttpRequestValidator()
        .addQueryParam("tournament_id", new MongoIdValidator)
        .addQueryParam("home_team_id", new MongoIdValidator)
        .addQueryParam("away_team_id", new MongoIdValidator)

    /**
     * Calculate teams strength based on previous results and
     * return probabilities between two teams in tournament
    */
    def getGameStats(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentId = context.request.getParam("tournament_id")
        var homeTeamId = context.request.getParam("home_team_id")
        var awayTeamId = context.request.getParam("away_team_id")
        var useActualGoals = true // true by default

        if (context.request.getParam("use_actual_goals") == Some("0")) {
            useActualGoals = false
        }

        var query = model.GameStats.getTeamsStrength(
            tournamentId.get, awayTeamId.get, homeTeamId.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                var teamsScoring: Array[Float] = null

                try {
                    teamsScoring = model.GameStats.getTeamsScoring(json, useActualGoals)
                    println(teamsScoring.mkString(" "))
                } catch {
                    case err: Throwable => {
                        logger.error(err.getStackTraceString)
                        val json = Json.obj(("error", err.toString))
                        jsonResponse(response, json)
                        context.fail(404)
                    }
                }

                if (teamsScoring != null) {
                    var totalDist = MLPNet.predict(teamsScoring, tournamentId.get + ".totals")
                    var scorelineDist = MLPNet.predict(teamsScoring, tournamentId.get + ".score")
                    var bttsDist = MLPNet.predict(teamsScoring, tournamentId.get + ".btts")

                    var bEv = new BettingEvents(scorelineDist, totalDist)

                    var draw = bEv.draw
                    var home = bEv.homeWin
                    var away = bEv.awayWin

                    var statsJson = Json.obj(
                        ("under 2.5", bEv._2_5._1),
                        ("over 2.5", bEv._2_5._2),
                        ("under 3.5", bEv._3_5._1),
                        ("over 3.5", bEv._3_5._2),
                        ("BTTS", bttsDist.last),
                        ("Home Win", home),
                        ("Away Win", away),
                        ("Draw", draw),
                        ("Home Double Chance", home + draw),
                        ("Away Double Chance", away + draw))

                    logger.info(context.request.path.get)
                    jsonResponse(response, statsJson)
                }

            }
            case Failure(cause) => {
                logger.error(cause.toString)
                logger.error(cause.getStackTraceString)
                context.fail(500)
            }
        }
    }
}