package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger
import io.vertx.lang.scala.json.Json

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global
import scala.math

import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.{jsonResponse, errorResponse}
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

        var teamsScoring: Array[Float] = null

        try {
            teamsScoring = model.GameStats.getTeamsScoring(json, false)
            println(teamsScoring.mkString(" "))
        } catch {
            case err: Throwable => {
                logger.error(err.toString)
                errorResponse(context.response, err.toString, 500)
            }
        }

        val modelId = model.TournamentModel.getTournamentModel(tournamentId.get).get
        var totalDist = MLPNet.predict(teamsScoring, model.TournamentModel.getTotalsModel(modelId))
        var scorelineDist = MLPNet.predict(teamsScoring, model.TournamentModel.getScorelineModel(modelId))
        var bttsDist = MLPNet.predict(teamsScoring, model.TournamentModel.getBttsModel(modelId))

        var bEv = new BettingEvents(scorelineDist, totalDist)

        var draw = bEv.draw
        var home = bEv.homeWin
        var away = bEv.awayWin

        var statsJson = Json.obj(
            ("under 2.5", math.min(totalDist.take(3).sum, bEv._2_5._1)),
            ("over 2.5", bEv._2_5._2),
            ("under 3.5", math.min(totalDist.take(4).sum, bEv._3_5._1)),
            ("over 3.5", bEv._3_5._2),
            ("BTTS", bttsDist.last),
            ("Home Win", home),
            ("Home Win +1.5", bEv.home_1_5),
            ("Home Win +2.5", bEv.home_2_5),
            ("Away Win", away),
            ("Away Win +1.5", bEv.away_1_5),
            ("Away Win +2.5", bEv.away_2_5),
            ("Draw", draw),
            ("Home Double Chance", home + draw),
            ("Away Double Chance", away + draw))

        logger.info(context.request.path.get)
        jsonResponse(response, statsJson)
    }
}
