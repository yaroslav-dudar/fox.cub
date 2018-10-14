package fox.cub.utils

import io.vertx.scala.core.http.HttpServerResponse
import io.vertx.core.json.JsonObject

object HttpUtils {
    def jsonResponse(resp: HttpServerResponse, data: JsonObject) {
        resp.putHeader("content-type", "application/json")
        resp.putHeader("Access-Control-Allow-Origin", "*")
        resp.setChunked(true)
        resp.write(data.encode).end()
    }
}
