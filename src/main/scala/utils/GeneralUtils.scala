package fox.cub.utils

import java.text.SimpleDateFormat
import java.util.TimeZone

object Utils {
    private val defaultDateFormat = "yyyy-MM-dd'T'HH:mm:ssXXX"

    def getUTCdate(dateFormat: String = defaultDateFormat) = {
        val df = new SimpleDateFormat(dateFormat)
        df.setTimeZone(TimeZone.getTimeZone("UTC"))
        df.format(System.currentTimeMillis)
    }

    def getDateByMillis(ms: Long,
                dateFormat: String = defaultDateFormat) = {

        val df = new SimpleDateFormat(dateFormat)
        df.setTimeZone(TimeZone.getTimeZone("UTC"))
        df.format(ms)
    }
}
