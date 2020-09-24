package fox.cub.router

import io.vertx.scala.ext.web.RoutingContext
import io.vertx.scala.core.eventbus.EventBus
import io.vertx.lang.scala.ScalaLogger
import io.vertx.core.eventbus.ReplyException
import io.vertx.scala.ext.auth.jwt.{JWTAuth}
import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject
import io.vertx.scala.core.http.HttpServerRequest

import java.security.MessageDigest
import java.util.Base64
import java.nio.charset.StandardCharsets

import scala.util.{Failure, Success}
import scala.concurrent.ExecutionContext.Implicits.global

import fox.cub.http.validator.{HttpRequestValidator, EnumValidator, MongoIdValidator}
import fox.cub.internals.ResultEvent
import fox.cub.utils.HttpUtils.{jsonResponse, errorResponse}
import fox.cub.db.DbProps
import fox.cub.model

object User {

    private val authPattern = "Bearer ([A-Za-z0-9-_=]+\\.[A-Za-z0-9-_=]+\\.?[A-Za-z0-9-_.+/=]*)".r
    val addNoteValidator = new HttpRequestValidator()
        .addJsonBodyParam("username", null, classOf[java.lang.String])
        .addJsonBodyParam("password", null, classOf[java.lang.String])

    private val digest = MessageDigest.getInstance("SHA-256");
    /**
     * Generate new JWT token
     */
    def login(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger, jwtProvider: JWTAuth) {
        var response = context.response
        var auth = context.getBodyAsJson.get
        var query = model.User.findUser(auth.getString("username"))

        val data = eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
            case Success(result) => {
                val user = model.User.getUser(result.body.result)
                if (user == None ) {
                    context.fail(401)
                }
                else if (!verifyPassword(user.get,  auth.getString("password"))) {
                    context.fail(401)
                }
                else {
                    var token = jwtProvider.generateToken(getJwtClaims(user.get))
                    println(getJwtClaims(user.get))
                    jsonResponse(response, Json.obj(("token", token)))
                }
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
      * Return list of user saved fixtures
      */
    def getFavorites(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        val userInfo = context.user().get.principal()

        var query = model.User.findUser(userInfo.getString("username"))
        eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
            case Success(result) => {
                val user = model.User.getUser(result.body.result)
                if (user == None ) {
                    context.fail(401)
                    return
                }

                var query = model.Fixtures.listByIds(user.get.getJsonArray("fav_fixtures"))

                eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
                    case Success(result) => {
                        val json = result.body.result
                        logger.info(context.request.path.get)
                        jsonResponse(response, json)
                    }
                    case Failure(cause) => {
                        logger.error(cause.toString)
                        context.fail(500)
                    }
                }
            }
            case Failure(cause) => {
                logger.error(cause.toString)
                context.fail(500)
            }
        }
    }

    /**
      * Add fixture to user favorites
      */
    def addFavFixture(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger) {
        var response = context.response
        var fixture = context.getBodyAsJson
        val userInfo = context.user().get.principal()

        var query = model.User.addFavFixture(userInfo.getString("username"),
                                             fixture.get.getString("fixture_id"))

        eb.sendFuture[ResultEvent](DbProps.QueueName, Option(query)).onComplete {
            case Success(result) => {
                val json = result.body.result
                logger.info(context.request.path.get)
                jsonResponse(response, json)
            }
            case Failure(cause) => {
                logger.error(cause.getStackTraceString)
                errorResponse(context.response, cause.toString, 500)
            }
        }
    }

    /**
      * Validate imput JWT token from request header
      *
      */
    def authentication(context: RoutingContext)(implicit eb: EventBus, logger: ScalaLogger, jwtProvider: JWTAuth) {
        val token = getToken(context.request())
        if (token == None) {
            context.fail(401)
        } else {
            val authInfo = Json.obj(("jwt", token.get))
            jwtProvider.authenticateFuture(authInfo).onComplete {
                case Success(user) => {
                    context.setUser(user)
                    context.next
                }
                case Failure(cause) => {
                    logger.error(cause.toString)
                    context.fail(401)
                }
            }
        }
    }

    def sha256(text: String): String = {
        val hash = digest.digest(text.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(hash);
    }

    def verifyPassword(user: JsonObject, password: String): Boolean = {
        val saltpass = password + user.getString("salt")
        if (sha256(saltpass) == user.getString("password")) return true
        return false
    }

    def getJwtClaims(user: JsonObject) = {
        Json.obj(
            ("username", user.getString(("username"))),
            ("notes", user.getJsonArray(("notes"))),
            ("fav_fixtures", user.getJsonArray(("fav_fixtures")))
        )
    }

    def getToken(req: HttpServerRequest) = {
        var auth = req.getHeader("Authorization")
        if (auth == None) {
            None
        } else {
            val token = authPattern.findAllIn(auth.get)
            if (token.isEmpty) None
            else Some(token.group(1))
        }

    }

}