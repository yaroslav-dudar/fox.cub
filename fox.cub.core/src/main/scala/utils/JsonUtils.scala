package fox.cub.utils

import io.vertx.core.json.JsonArray
import scala.collection.mutable.ListBuffer

object JsonUtils {
    def arrayToBuffer[A](arr: JsonArray): ListBuffer[A] = {
        var list = new ListBuffer[A]()
        arr.forEach(v => {list += v.asInstanceOf[A]})
        list
    }

    def getArrayOfNumbers(arr: JsonArray): ListBuffer[Double] = {
        var list = new ListBuffer[Double]()
        arr.forEach(v => {
            v match {
                case _: java.lang.Integer => list += v.asInstanceOf[Int].toDouble
                case _: java.lang.Double => list += v.asInstanceOf[Double]
                case _: java.lang.String => list += v.asInstanceOf[String].toDouble
            }
        })
        list
    }
}
