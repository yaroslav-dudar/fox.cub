package fox.cub.http

import io.vertx.lang.scala.{ScalaVerticle}
import io.vertx.scala.config.{ConfigStoreOptions, ConfigRetriever}

import scala.concurrent.Future

/**
 * Http server component
*/
class HttpVerticle extends ScalaVerticle {
    private val HttpConfigs = "restapi"

    override def startFuture(): Future[Unit] = {
        var retriever = ConfigRetriever.create(vertx)

        retriever.getConfigFuture.flatMap(config => {
            var router = new HttpRouter(vertx, config).router
            var apiConfig = config.getJsonObject(HttpConfigs)

            vertx
                .createHttpServer()
                .requestHandler(router.accept)
                .listenFuture(
                    apiConfig.getInteger("port"),
                    apiConfig.getString("host")
                )
                .map(_ => ())
        })
    }
}
