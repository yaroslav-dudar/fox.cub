package fox.cub.utils

import io.vertx.scala.core.http.HttpServerResponse
import io.vertx.core.json.JsonObject

object HttpUtils {
    var crossHeadersAllowed = "X-Requested-With, Content-Type, Authorization"

    def jsonResponse(resp: HttpServerResponse, data: JsonObject) {
        resp.putHeader("content-type", "application/json")
            .setChunked(true)
            .write(data.encode)
            .end()
    }

    def errorResponse(resp: HttpServerResponse, errmsg: String, errcode: Int = 500) {
        val err = new JsonObject().put("error", errmsg)
        resp.setStatusCode(errcode)
            .putHeader("content-type", "application/json")
            .setChunked(true)
            .write(err.encode)
            .end()
    }

    def errorResponse(resp: HttpServerResponse, errmsg: JsonObject, errcode: Int) {
        val err = new JsonObject().put("error", errmsg)
        resp.setStatusCode(errcode)
            .putHeader("content-type", "application/json")
            .setChunked(true)
            .write(err.encode)
            .end()
    }
}
