package fox.cub.utils

import io.vertx.core.json.JsonArray

import scala.collection.mutable.ListBuffer

object JsonUtils {
    def arrayToBuffer[A](arr: JsonArray): ListBuffer[A] = {
        var list = new ListBuffer[A]()
        arr.forEach(v => {list += v.asInstanceOf[A]})
        list
    }
}
