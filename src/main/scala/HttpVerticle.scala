package fox.cub.http

import io.vertx.lang.scala.ScalaVerticle
import io.vertx.scala.config.{ConfigStoreOptions, ConfigRetriever}

import scala.concurrent.{Future, Await}
import scala.util.{Failure, Success}
import io.vertx.lang.scala.ScalaLogger

class HttpVerticle extends ScalaVerticle {

  private val logger = ScalaLogger.getLogger(this.getClass.getName)

  override def startFuture(): Future[Unit] = {
    var retriever = ConfigRetriever.create(vertx)
  
    retriever.getConfigFuture.flatMap(config => {
        var router = new HttpRouter(vertx, config).router
        var apiConfig = config.getJsonObject("restapi")
      
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
