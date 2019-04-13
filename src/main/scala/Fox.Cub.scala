package fox.cub

import io.vertx.scala.core.Vertx

object FoxCub {

    private val vertx = Vertx.vertx

    def main(args: Array[String]): Unit = {
        // startup http server
        vertx.deployVerticle("scala:fox.cub.http.HttpVerticle")
        // stratup db verticle
        vertx.deployVerticle("scala:fox.cub.db.DatabaseVerticle")
    }
}
