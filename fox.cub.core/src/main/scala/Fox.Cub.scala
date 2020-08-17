package fox.cub

import io.vertx.scala.core.Vertx
import io.vertx.core.DeploymentOptions
import io.vertx.scala.core.{DeploymentOptions => SDeploymentOptions}

object FoxCub {

    private val vertx = Vertx.vertx

    def main(args: Array[String]): Unit = {
        // startup http server
        val options = new SDeploymentOptions(new DeploymentOptions()).setInstances(4);
        vertx.deployVerticle("scala:fox.cub.http.HttpVerticle", options)
        // stratup db verticle
        vertx.deployVerticle("scala:fox.cub.db.DatabaseVerticle")
    }
}
