package fox.cub.http

import io.vertx.scala.ext.web.{Router, RoutingContext}
import io.vertx.scala.ext.mongo.MongoClient
import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.ScalaLogger

import io.vertx.scala.core.Vertx

class HttpRouter(vertx: Vertx, config: JsonObject) {
    private val DbSettings = "database"
    // init logger
    private val logger = ScalaLogger.getLogger(this.getClass.getName)
    private val _router = Router.router(vertx)

    // db client
    var client = MongoClient.createShared(
        vertx,
        config.getJsonObject(DbSettings),
        "REST_API_POOL")

    router.get("/").handler(indexRoute)

    def router = _router

    def indexRoute(context: RoutingContext ) {
        val json = new JsonObject().put("version", "0.0.1").encode
        var response = context.response

        logger.info(context.request.path.get)

        response.putHeader("content-type", "application/json")
        response.setChunked(true)
        response.write(json).end()
    }
}
