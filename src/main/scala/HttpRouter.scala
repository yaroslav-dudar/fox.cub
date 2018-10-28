package fox.cub.http

import io.vertx.scala.ext.web.Router
import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.ScalaLogger
import io.vertx.scala.core.Vertx
import io.vertx.core.eventbus.EventBus
import io.vertx.scala.ext.web.handler.BodyHandler

import fox.cub.internals.{QueryEvent, QueryEventCodec}
import fox.cub.internals.{ResultEvent, ResultEventCodec}

import fox.cub.router.{
    GameOdds => RouterGameOdds,
    GameStats => RouterGameStats,
    Team => RouterTeam,
    Tournament => RouterTournament
}

/**
 * Setup web routers and handlers
*/
class HttpRouter(vertx: Vertx, config: JsonObject) {

    implicit private val logger = ScalaLogger.getLogger(this.getClass.getName)
    private val _router = Router.router(vertx)
    implicit private val eb = vertx.eventBus()

    // register custom message codecs
    eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
        classOf[QueryEvent], new QueryEventCodec())
    eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
        classOf[ResultEvent], new ResultEventCodec())

    router.route().handler(BodyHandler.create())

    router.get("/api/v1/game").handler(RouterTeam.getGames)
    router.get("/api/v1/team/:tournament_id").handler(RouterTournament.getTournamentTeams)
    router.get("/api/v1/tournament").handler(RouterTournament.getTournamentsList)

    router.get("/api/v1/stats/:tournament_id")
        .handler(RouterGameStats.getGameStatsValidator.handle)
        .handler(RouterGameStats.getGameStats)

    router.get("/api/v1/odds/:tournament_id")
        .handler(RouterGameOdds.getOddsValidator.handle)
        .handler(RouterGameOdds.getOdds)

    def router = _router
}
