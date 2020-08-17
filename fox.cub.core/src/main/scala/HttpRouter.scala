package fox.cub.http

import io.vertx.scala.ext.web.Router
import io.vertx.lang.scala.ScalaLogger
import io.vertx.scala.core.Vertx
import io.vertx.scala.ext.web.handler.{BodyHandler, CorsHandler}

import io.vertx.scala.ext.auth.jwt.{JWTAuthOptions, JWTAuth}
import io.vertx.scala.ext.auth.KeyStoreOptions

import io.vertx.core.eventbus.EventBus
import io.vertx.core.json.JsonObject
import io.vertx.core.http.HttpMethod

import fox.cub.internals.{QueryEvent, QueryEventCodec}
import fox.cub.internals.{ResultEvent, ResultEventCodec}

import scala.collection.mutable.SortedSet

import fox.cub.router.{
    GameStats => RouterGameStats,
    Team => RouterTeam,
    Tournament => RouterTournament,
    UserNotes => RouterUserNotes,
    StatisticalModel => RouterModel,
    Fixtures => RouterFixtures,
    Odds => RouterOdds,
    Market => RouterMarket,
    User => RouterUser
}

/**
 * Setup web routers and handlers
*/
class HttpRouter(vertx: Vertx, config: JsonObject) {

    implicit private val logger = ScalaLogger.getLogger(this.getClass.getName)
    private val _router = Router.router(vertx)
    implicit private val eb = vertx.eventBus()
    private val crossHeadersAllowed = SortedSet("Content-Type", "X-Requested-With")

    private var jwtOpt = JWTAuthOptions()
        .setKeyStore(KeyStoreOptions()
            .setPath(config.getJsonObject("jwt").getString("keypath"))
            .setType("jceks")
            .setPassword(config.getJsonObject("jwt").getString("keypwd")))

    implicit private val jwtProvider = JWTAuth.create(vertx, jwtOpt);

    registerMsgCodec()

    router.route().handler(BodyHandler.create()
        .setDeleteUploadedFilesOnEnd(true))

    router.route().handler(
        CorsHandler.create("*")
            .allowedMethod(HttpMethod.GET)
            .allowedMethod(HttpMethod.POST)
            .allowedHeaders(crossHeadersAllowed)
    )

    router.get("/api/v1/game").handler(RouterTeam.getGames)
    router.get("/api/v1/team/:tournament_id").handler(RouterTournament.getTournamentTeams)
    router.get("/api/v1/tournament").handler(RouterTournament.getTournamentsList)
    router.get("/api/v1/tournament/home_adv/:tournament_id")
        .handler(RouterTournament.getTournamentHomeAdvanatage)
    router.get("/api/v1/tournament/:tournament_id")
        .handler(RouterTournament.getTournamentTable)

    router.get("/api/v1/stats/:tournament_id")
        .handler(RouterGameStats.getGameStatsValidator.handle)
        .handler(RouterGameStats.getGameStats)

    router.post("/api/v1/note")
        .handler(RouterUserNotes.addNoteValidator.handle)
        .handler(RouterUserNotes.addNote)

    router.get("/api/v1/note/:ref_id")
        .handler(RouterUserNotes.getNoteValidator.handle)
        .handler(RouterUserNotes.getNotes)

    router.post("/api/v1/model/stats").handler(RouterModel.getGameStats)
    router.post("/api/v1/model/train")
        .handler(RouterModel.trainModelValidator.handle)
        .handler(RouterModel.trainModel)

    router.get("/api/v1/fixtures")
        .handler(RouterFixtures.fixturesListValidator.handle)
        .handler(RouterFixtures.list)

    router.get("/api/v1/market/tournaments")
        .handler(RouterMarket.getTournaments)
    router.get("/api/v1/market/teams")
        .handler(RouterMarket.getTeams)
    router.get("/api/v1/market/movement")
        .handler(RouterFixtures.fixturesListValidator.handle)
        .handler(RouterMarket.getMarketMoves)


    router.get("/api/v2/odds")
        .handler(RouterOdds.getOddsValidator.handle)
        .handler(RouterOdds.getOdds)

    router.get("/api/v2/odds/diff")
        .handler(RouterOdds.getOddsValidator.handle)
        .handler(RouterOdds.getDiff)

    router.post("/api/v1/auth/login")
        .handler(RouterUser.login)

    router.get("/api/v1/user/favorites")
        .handler(RouterUser.authentication)
        .handler(RouterUser.getFavorites)

    def router = _router

    /**
     * Registering default message codec for Event Bus
    */
    def registerMsgCodec() {
        try {
            eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
                classOf[QueryEvent], new QueryEventCodec())
            eb.asJava.asInstanceOf[EventBus].registerDefaultCodec(
                classOf[ResultEvent], new ResultEventCodec())
        } catch {
            case e: java.lang.IllegalStateException => {
                logger.warn(s"Message codec already registered: $e")
            }
        }
    }
}
