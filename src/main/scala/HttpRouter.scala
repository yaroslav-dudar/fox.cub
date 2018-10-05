package fox.cub.http

import io.vertx.scala.ext.web.{Router, RoutingContext}
import io.vertx.scala.ext.mongo.MongoClient
import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.ScalaLogger
import io.vertx.lang.scala.json.Json
import io.vertx.scala.core.Vertx
import io.vertx.scala.core.eventbus.Message
import io.vertx.core.eventbus.{EventBus, ReplyException}

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.internals.{QueryEvent, QueryEventCodec}
import fox.cub.internals.{ResultEvent, ResultEventCodec}

import fox.cub.model.{GameStats, Team, Tournament}
import fox.cub.math.CMP
import fox.cub.betting.BettingEvents

/**
 * Web routers, handlers
*/
class HttpRouter(vertx: Vertx, config: JsonObject) {
    private val DbQueueName = "db.queue"
    // init logger
    private val logger = ScalaLogger.getLogger(this.getClass.getName)
    private val _router = Router.router(vertx)

    private val eb = vertx.eventBus()

    // register custom message codecs
    eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
        classOf[QueryEvent], new QueryEventCodec())
    eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
        classOf[ResultEvent], new ResultEventCodec())

    router.get("/api/v1/game/:team_id").handler(getGames)
    router.get("/api/v1/team/:tournament_id").handler(getTournamentTeams)
    router.get("/api/v1/tournament").handler(getTournaments)
    router.get("/api/v1/stats/:tournament_id").handler(getGameStats)

    def router = _router

    def getGames(context: RoutingContext) {
        var response = context.response
        var team = context.request.getParam("team_id")
        var query = GameStats.get(team.get)

        val data = eb.sendFuture[ResultEvent](DbQueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result.encode

                logger.info(context.request.path.get)
                response.putHeader("content-type", "application/json")
                response.putHeader("Access-Control-Allow-Origin", "*")
                response.setChunked(true)
                response.write(json).end()
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                context.fail(500)
            }
        }
    }

    def getTournamentTeams(context: RoutingContext) {
        var response = context.response
        var tournament = context.request.getParam("tournament_id")
        var query = Team.getByTournament(tournament.get)

        val data = eb.sendFuture[ResultEvent](DbQueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result.encode

                logger.info(context.request.path.get)
                response.putHeader("content-type", "application/json")
                response.putHeader("Access-Control-Allow-Origin", "*")
                response.setChunked(true)
                response.write(json).end()
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                context.fail(500)
            }
        }
    }

    def getGameStats(context: RoutingContext) {
        var response = context.response
        var tournamentId = context.request.getParam("tournament_id")
        var homeTeamId = context.request.getParam("home_team_id")
        var awayTeamId = context.request.getParam("away_team_id")
        var query = GameStats.getTeamsStrength(tournamentId.get, awayTeamId.get, homeTeamId.get)
        var cmp = new CMP()
        val data = eb.sendFuture[ResultEvent](DbQueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result
                var matchupStr: Tuple2[Float, Float] = null

                try {
                    matchupStr = GameStats.getTeamsStrength(json)
                } catch {
                    case err: Throwable => {
                        logger.error(err.toString)
                        val json = Json.obj(("error", err.toString))
                        response.putHeader("content-type", "application/json")
                        response.putHeader("Access-Control-Allow-Origin", "*")
                        response.setChunked(true)
                        response.write(json.encode).end()
                        context.fail(404)
                    }
                }

                if (matchupStr != null) {
                    var homeDist = cmp.adjustedDistRange(matchupStr._1, 1)
                    var awayDist = cmp.adjustedDistRange(matchupStr._2, 1)

                    var bEv = new BettingEvents(homeDist, awayDist)

                    var draw = bEv.draw
                    var home = bEv.homeWin
                    var away = bEv.awayWin
                    println(json)

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
                    response.putHeader("content-type", "application/json")
                    response.putHeader("Access-Control-Allow-Origin", "*")
                    response.setChunked(true)
                    response.write(statsJson.encode).end()
                }

            }
            case Failure(cause) => {
                logger.error(cause.toString)
                context.fail(500)
            }
        }
    }

    def getTournaments(context: RoutingContext) {
        var response = context.response
        var query = Tournament.getAll()

        val data = eb.sendFuture[ResultEvent](DbQueueName, query).onComplete {
            case Success(result) => {
                val json = result.body.result.encode

                logger.info(context.request.path.get)
                response.putHeader("content-type", "application/json")
                response.putHeader("Access-Control-Allow-Origin", "*")
                response.setChunked(true)
                response.write(json).end()
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                context.fail(500)
            }
        }
    }
}
