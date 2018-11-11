package fox.cub.model

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.internals.QueryEvent
import fox.cub.utils.Utils.getUTCdate


object UserNote {
    private val Collection = "user_notes"
    // TODO: implement authentication and remove hardcoded user
    private val DEFAULT_USER = "1"

    def getNotes(userId: String, refTo: String, refId: String): QueryEvent = {
        val filter = Json.obj(("user", DEFAULT_USER), ("ref_id", refId), ("ref_to", refTo))
        val query = new JsonObject().put("find", Collection).put("filter", filter)
        QueryEvent("find", query)
    }

    def save(note: JsonObject): QueryEvent = {
        var createdAt = Json.obj(("$date", getUTCdate()))

        val document = Json.obj(
            ("user", DEFAULT_USER),
            ("ref_id", note.getString("ref_id")),
            ("ref_to", note.getString("ref_to")),
            ("created_at", createdAt),
            ("updated_at", createdAt),
            ("note_text", note.getString("note_text")),
            ("note_type", note.getString("note_type"))
        )

        val query = new JsonObject()
            .put("insert", Collection)
            .put("documents", Json.arr(document))

        QueryEvent("insert", query)
    }
}
