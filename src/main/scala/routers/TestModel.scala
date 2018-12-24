package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger
import io.vertx.lang.scala.json.Json

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global
import scala.math

import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.jsonResponse
import fox.cub.db.DbProps
import fox.cub.model
import fox.cub.math.CMP
import fox.cub.betting.BettingEvents
import fox.cub.http.validator.{HttpRequestValidator, MongoIdValidator}
import fox.cub.net.MLPNet

object TestModel {

    /**
     * Using for testing only
    */
    def getGameStats(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var tournamentId = context.request.getParam("tournament_id")
        var json = context.getBodyAsJson.get

        var matchupStr: Tuple2[Float, Float] = null

        try {
            matchupStr = model.GameStats.getTeamsStrength(json)
        } catch {
            case err: Throwable => {
                logger.error(err.toString)
                val json = Json.obj(("error", err.toString))
                jsonResponse(response, json)
                context.fail(404)
            }
        }

        val teamsScoring = model.GameStats.getTeamsScoring(json)
        println(teamsScoring)
        var homeDist = CMP.adjustedDistRange(matchupStr._1, 1)
        var awayDist = CMP.adjustedDistRange(matchupStr._2, 1)
        var totalDist = MLPNet.predict(teamsScoring, tournamentId.get + ".totals")

        var bEv = new BettingEvents(homeDist, awayDist, totalDist)

        var draw = bEv.draw
        var home = bEv.homeWin
        var away = bEv.awayWin

        var statsJson = Json.obj(
            ("under 2.5", math.min(totalDist.take(3).sum, bEv._2_5._1)),
            ("over 2.5", bEv._2_5._2),
            ("under 3.5", math.min(totalDist.take(4).sum, bEv._3_5._1)),
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
