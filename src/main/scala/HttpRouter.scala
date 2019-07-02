package fox.cub.http

import io.vertx.scala.ext.web.Router
import io.vertx.lang.scala.ScalaLogger
import io.vertx.scala.core.Vertx
import io.vertx.scala.ext.web.handler.{BodyHandler, CorsHandler}

import io.vertx.core.eventbus.EventBus
import io.vertx.core.json.JsonObject
import io.vertx.core.http.HttpMethod

import fox.cub.internals.{QueryEvent, QueryEventCodec}
import fox.cub.internals.{ResultEvent, ResultEventCodec}

import scala.collection.mutable.SortedSet

import fox.cub.router.{
    GameOdds => RouterGameOdds,
    GameStats => RouterGameStats,
    Team => RouterTeam,
    Tournament => RouterTournament,
    UserNotes => RouterUserNotes,
    TestModel => RouterTestModel,
    Fixtures => RouterFixtures,
    Odds => RouterOdds
}

/**
 * Setup web routers and handlers
*/
class HttpRouter(vertx: Vertx, config: JsonObject) {

    implicit private val logger = ScalaLogger.getLogger(this.getClass.getName)
    private val _router = Router.router(vertx)
    implicit private val eb = vertx.eventBus()
    private val crossHeadersAllowed = SortedSet("Content-Type", "X-Requested-With")

    // register custom message codecs
    eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
        classOf[QueryEvent], new QueryEventCodec())
    eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
        classOf[ResultEvent], new ResultEventCodec())

    router.route().handler(BodyHandler.create())
    router.route().handler(
        CorsHandler.create("*")
            .allowedMethod(HttpMethod.GET)
            .allowedMethod(HttpMethod.POST)
            .allowedHeaders(crossHeadersAllowed)
    )

    router.get("/api/v1/game").handler(RouterTeam.getGames)
    router.get("/api/v1/team/:tournament_id").handler(RouterTournament.getTournamentTeams)
    router.get("/api/v1/tournament").handler(RouterTournament.getTournamentsList)
    router.get("/api/v1/tournament/:tournament_id").handler(RouterTournament.getTournamentTable)

    router.get("/api/v1/stats/:tournament_id")
        .handler(RouterGameStats.getGameStatsValidator.handle)
        .handler(RouterGameStats.getGameStats)

    router.get("/api/v1/odds/:tournament_id")
        .handler(RouterGameOdds.getOddsValidator.handle)
        .handler(RouterGameOdds.getOdds)

    router.post("/api/v1/note")
        .handler(RouterUserNotes.addNoteValidator.handle)
        .handler(RouterUserNotes.addNote)

    router.get("/api/v1/note/:ref_id")
        .handler(RouterUserNotes.getNoteValidator.handle)
        .handler(RouterUserNotes.getNotes)

    router.post("/api/v1/test/stats").handler(RouterTestModel.getGameStats)

    router.get("/api/v1/fixtures").handler(RouterFixtures.getFixtures)
    router.get("/api/v2/odds/:fixture_id")
        .handler(RouterOdds.getOddsValidator.handle)
        .handler(RouterOdds.getOdds)

    def router = _router
}
