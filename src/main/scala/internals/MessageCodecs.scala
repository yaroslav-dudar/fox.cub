package fox.cub.internals

import io.vertx.core.eventbus.MessageCodec
import io.vertx.core.buffer.Buffer
import io.vertx.core.json.JsonObject
import io.vertx.lang.scala.json.Json

case class QueryEvent(command: String, query: JsonObject)
case class ResultEvent(result: JsonObject)

class ResultEventCodec extends MessageCodec[ResultEvent, ResultEvent] {
    val resField = "result"

    override def encodeToWire(buffer: Buffer, ev: ResultEvent) {
        var jsonToEncode = Json.obj((resField, ev.result))

        val jsonToStr = jsonToEncode.encode
        val length = jsonToStr.getBytes.length
    
        buffer.appendInt(length)
        buffer.appendString(jsonToStr)
    }

    override def decodeFromWire(pos: Int, buffer: Buffer): ResultEvent = {
        var _pos = pos
        // Length of JSON
        val length = buffer.getInt(_pos)
        val json = new JsonObject(buffer.getString(_pos+4, _pos+length))

        ResultEvent(
            json.getJsonObject(resField),
        )
    }

    override def transform(ev: ResultEvent): ResultEvent =  {
        ev
    }

    override def systemCodecID(): Byte = {
        -1
    }

    override def name(): String = {
        this.getClass.getName
    }
}

class QueryEventCodec extends MessageCodec[QueryEvent, QueryEvent] {
    val commandField = "command"
    val queryField = "query"

    override def encodeToWire(buffer: Buffer, ev: QueryEvent) {
        var jsonToEncode = Json.obj(
            (commandField, ev.command),
            (queryField, ev.query))

        val jsonToStr = jsonToEncode.encode
        val length = jsonToStr.getBytes.length
    
        buffer.appendInt(length)
        buffer.appendString(jsonToStr)
    }

    override def decodeFromWire(pos: Int, buffer: Buffer): QueryEvent = {
        var _pos = pos
        // Length of JSON
        val length = buffer.getInt(_pos)
        val json = new JsonObject(buffer.getString(_pos+4, _pos+length))

        QueryEvent(
            json.getString(commandField),
            json.getJsonObject(queryField)
        )
    }

    override def transform(ev: QueryEvent): QueryEvent =  {
        ev
    }

    override def systemCodecID(): Byte = {
        -1
    }

    override def name(): String = {
        this.getClass.getName
    }
}
