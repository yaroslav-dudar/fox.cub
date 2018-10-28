package fox.cub.http.validator

import scala.collection.mutable.HashMap
import scala.util.matching.Regex
import io.vertx.lang.scala.ScalaLogger
import io.vertx.scala.ext.web.RoutingContext
import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject

import fox.cub.utils.HttpUtils.jsonResponse

abstract class BaseTypeValidator() {
    def isValid(fieldValue: Option[String], fieldName: String)
}

class RegexValidator(pattern: String) extends BaseTypeValidator {
    def isValid(fieldValue: Option[String], fieldName: String) {
        if (fieldValue.nonEmpty) {
            if (!fieldValue.get.matches(pattern)) {
                throw new HttpRequestValidatorException(
                    s"$fieldName parameter: regex not match")
            }
        }
    }
}

class MongoIdValidator() extends RegexValidator("^[a-f\\d]{24}$") {}

final case class HttpRequestValidatorException(
    private val message: String = "", 
    private val cause: Throwable = None.orNull) extends Exception(message, cause)

class ParameterValidationRule(field: Option[String], fieldName: String,
    rule: BaseTypeValidator, isOptional: Boolean = false) {
    
    if (!isOptional) isExists
    rule.isValid(field, fieldName)

    def isExists() {
        if (field.isEmpty) {
            throw new HttpRequestValidatorException(s"Query parameter: $fieldName not exists")
        }
    }
}

class HttpRequestValidator {

    val queryParamRules = HashMap[String, BaseTypeValidator]()
    var errors = new JsonObject()

    def addQueryParam(fieldName: String, rule: BaseTypeValidator): this.type = {
        queryParamRules += (fieldName -> rule)
        this
    }

    def handle(context: RoutingContext)(implicit logger: ScalaLogger) {
        for ((fieldName, rule) <- queryParamRules) {
            var field = context.request.getParam(fieldName)
            try {
                new ParameterValidationRule(field, fieldName, rule)
            } catch {
                case e: Throwable => {
                    logger.error(e.toString)
                    errors.put(fieldName, e.toString)
                }
            }
            
        }

        if (!errors.isEmpty) {
            jsonResponse(context.response, Json.obj(("error", errors)))
            context.fail(400)
        } else {
            context.next
        }
    }
}
