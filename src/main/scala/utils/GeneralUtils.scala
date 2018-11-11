package fox.cub.utils

import java.text.SimpleDateFormat
import java.util.TimeZone

object Utils {
    def getUTCdate(dateFormat: String = "yyyy-MM-dd'T'HH:mm:ssXXX") = {
        val df = new SimpleDateFormat(dateFormat)
        df.setTimeZone(TimeZone.getTimeZone("UTC"))
        df.format(System.currentTimeMillis)
    }
}
