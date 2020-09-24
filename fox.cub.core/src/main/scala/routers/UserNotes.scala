package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger
import io.vertx.core.eventbus.ReplyException

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.http.validator.{HttpRequestValidator, EnumValidator, MongoIdValidator}
import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.{jsonResponse, errorResponse}
import fox.cub.db.DbProps
import fox.cub.model

object UserNotes {

    val noteTypes = List("review", "weakness", "strength", "general")
    val refTo = List("team", "player", "tournament", "game")

    val addNoteValidator = new HttpRequestValidator()
        .addJsonBodyParam("note_type", new EnumValidator(noteTypes), classOf[java.lang.String])
        .addJsonBodyParam("ref_to", new EnumValidator(refTo), classOf[java.lang.String])
        .addJsonBodyParam("note_text", null, classOf[java.lang.String])
        .addJsonBodyParam("ref_id", new MongoIdValidator, classOf[java.lang.String])

    val getNoteValidator = new HttpRequestValidator()
        .addQueryParam("ref_to", new EnumValidator(refTo))
        .addQueryParam("user_id", null)
        .addQueryParam("ref_id", new MongoIdValidator)

    /**
     * Add new user note
    */
    def addNote(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var note = context.getBodyAsJson
        var query = model.UserNote.save(note.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause: ReplyException) => {
                logger.error(cause.toString)
                errorResponse(response, cause.getMessage, cause.failureCode)
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                errorResponse(response, cause.toString)
            }
        }
    }

    /**
     * Add new user note
    */
    def getNotes(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var user = context.request.getParam("user_id")
        var refId = context.request.getParam("ref_id")
        var refTo = context.request.getParam("ref_to")
        var query = model.UserNote.getNotes(user.get, refTo.get, refId.get)

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause: ReplyException) => {
                logger.error(cause.toString)
                errorResponse(response, cause.getMessage, cause.failureCode)
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                errorResponse(response, cause.toString)
            }
        }
    }
}