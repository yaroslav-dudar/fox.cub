package fox.cub.http

import io.vertx.lang.scala.{ScalaVerticle, ScalaLogger}
import io.vertx.scala.config.{ConfigStoreOptions, ConfigRetriever}

import scala.concurrent.Future

import fox.cub.net.MLPNet
import java.io.File

/**
 * Http server component
*/
class HttpVerticle extends ScalaVerticle {
    private val HttpConfigs = "restapi"
    private val logger = ScalaLogger.getLogger(this.getClass.getName)

    override def startFuture(): Future[Unit] = {
        var retriever = ConfigRetriever.create(vertx)

        retriever.getConfigFuture.flatMap(config => {
            var router = new HttpRouter(vertx, config).router
            var apiConfig = config.getJsonObject(HttpConfigs)
            var mlpPath = apiConfig.getString("mlp_models_dir")

            vertx.executeBlocking(() => {
                // setup MLP networks
                new java.io.File(mlpPath)
                    .listFiles.map(f => MLPNet.loadModel(f.getAbsolutePath))
            })


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
