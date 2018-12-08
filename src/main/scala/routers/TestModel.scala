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

object TestModel {

    /**
     * Using for testing only
    */
    def getGameStats(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
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

        val mutchupTotal = model.GameStats.getTeamsScoring(json)
        println(mutchupTotal)
        var homeDist = CMP.adjustedDistRange(matchupStr._1, mutchupTotal._2)
        var awayDist = CMP.adjustedDistRange(matchupStr._2, mutchupTotal._2)
        var totalDist = CMP.distRange(mutchupTotal._1, mutchupTotal._2, 8)

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
