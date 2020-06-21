package fox.cub.utils

import java.text.SimpleDateFormat
import java.util.TimeZone

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
}
