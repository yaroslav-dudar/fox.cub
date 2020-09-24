package fox.cub.utils

import java.text.SimpleDateFormat
import java.util.TimeZone

import scala.collection.mutable.ListBuffer

import io.vertx.scala.config.{ConfigStoreOptions, ConfigRetriever, ConfigRetrieverOptions}
import io.vertx.core.json.{JsonObject, JsonArray}

object Utils {
    private val mongoDateFormat = "yyyy-MM-dd'T'HH:mm:ssXXX";
    private val webApiDateFormat = "yyyy-MM-dd";

    def getUTCdate(dateFormat: String = mongoDateFormat) = {
        val df = new SimpleDateFormat(dateFormat)
        df.setTimeZone(TimeZone.getTimeZone("UTC"))
        df.format(System.currentTimeMillis)
    }

    def getDateByMillis(ms: Long,
                        dateFormat: String = mongoDateFormat) = {

        val df = new SimpleDateFormat(dateFormat)
        df.setTimeZone(TimeZone.getTimeZone("UTC"))
        df.format(ms)
    }

    def getTimeMillisByStr(dateStr: String,
                          dateFormat: String = webApiDateFormat) = {

        val df = new SimpleDateFormat(dateFormat)
        df.setTimeZone(TimeZone.getTimeZone("UTC"))
        df.parse(dateStr).getTime
    }

    def getConfigOptions() = {
        var dirStore = ConfigStoreOptions()
            .setType("directory")
            .setConfig(new JsonObject()
                .put("path", System.getenv("APP_CONFIG"))
                .put("filesets", new JsonArray()
                .add(new JsonObject()
                    .put("pattern", "*json"))))

        ConfigRetrieverOptions()
            .setStores(ListBuffer(dirStore))
    }
}
