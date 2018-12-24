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
        var query = model.GameStats.getTeamsStrength(
            tournamentId.get, awayTeamId.get, homeTeamId.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                var matchupStr: Tuple2[Float, Float] = null
                var teamsScoring: Array[Float] = null

                try {
                    matchupStr = model.GameStats.getTeamsStrength(json)
                    teamsScoring = model.GameStats.getTeamsScoring(json)
                    println(teamsScoring.mkString(" "))
                } catch {
                    case err: Throwable => {
                        logger.error(err.toString)
                        val json = Json.obj(("error", err.toString))
                        jsonResponse(response, json)
                        context.fail(404)
                    }
                }

                if (matchupStr != null) {
                    var homeDist = CMP.adjustedDistRange(matchupStr._1, 1)
                    var awayDist = CMP.adjustedDistRange(matchupStr._2, 1)
                    var totalDist = MLPNet.predict(teamsScoring, tournamentId.get + ".totals")

                    var bEv = new BettingEvents(homeDist, awayDist, totalDist)

                    var draw = bEv.draw
                    var home = bEv.homeWin
                    var away = bEv.awayWin

                    var statsJson = Json.obj(
                        ("under 2.5", bEv._2_5._1),
                        ("over 2.5", bEv._2_5._2),
                        ("under 3.5", bEv._3_5._1),
                        ("over 3.5", bEv._3_5._2),
                        ("BTTS", bEv.btts),
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
                context.fail(500)
            }
        }
    }
}