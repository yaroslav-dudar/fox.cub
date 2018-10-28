package fox.cub.utils

import io.vertx.scala.core.http.HttpServerResponse
import io.vertx.core.json.JsonObject

object HttpUtils {
    def jsonResponse(resp: HttpServerResponse, data: JsonObject) {
        resp.putHeader("content-type", "application/json")
            .putHeader("Access-Control-Allow-Origin", "*")
            .setChunked(true)
            .write(data.encode)
            .end()
    }
}
