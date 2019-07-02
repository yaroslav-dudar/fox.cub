package fox.cub.http.validator

import scala.collection.mutable.HashMap
import scala.util.matching.Regex
import io.vertx.lang.scala.ScalaLogger
import io.vertx.scala.ext.web.RoutingContext
import io.vertx.lang.scala.json.Json
import io.vertx.core.json.{JsonObject, DecodeException}

import fox.cub.utils.HttpUtils.errorResponse

abstract class BaseTypeValidator() {
    def isValid[T](fieldValue: Option[T], fieldName: String)
}

class RegexValidator(pattern: String) extends BaseTypeValidator {
    def isValid[T](fieldValue: Option[T], fieldName: String) {
        if (fieldValue.nonEmpty) {
            var v = fieldValue.get.toString
            if (!v.matches(pattern)) {
                throw new HttpRequestValidatorException(
                    s"Parameter $fieldName regex not match to pattern: $pattern")
            }
        }
    }
}

class EnumValidator[T](acceptableValues: Seq[T]) extends BaseTypeValidator {
    def isValid[T](fieldValue: Option[T], fieldName: String) {
         if (fieldValue.nonEmpty) {
            if (!acceptableValues.contains(fieldValue.get)) {
                throw new HttpRequestValidatorException(
                    s"Parameter $fieldName should be one of $acceptableValues")
            }
         }
    }
}

class MongoIdValidator() extends RegexValidator("^[a-f\\d]{24}$") {}

final case class HttpRequestValidatorException(
    private val message: String = "",
    private val cause: Throwable = None.orNull) extends Exception(message, cause)

class RuleValidator(field: Option[Object], fieldName: String,
    rule: BaseTypeValidator, isOptional: Boolean = false,
    fieldType: Class[_] = classOf[java.lang.String]) {

    if (!isOptional) isExists
    checkType
    if (rule != null) rule.isValid(field, fieldName)

    /**
     * Validate existence of a given field value
    */
    def isExists() {
        if (field == None) {
            throw new HttpRequestValidatorException(s"Parameter $fieldName not exists")
        }
    }

    /**
     * Validate field type
    */
    def checkType() {
        if (field.nonEmpty) {
            if (field.get.getClass != fieldType) {
                throw new HttpRequestValidatorException(
                    s"Parameter $fieldName should have type $fieldType")
            }
        }
    }
}

class HttpRequestValidator {

    val queryParamRules = HashMap[String, BaseTypeValidator]()
    val jsonBodyRules = HashMap[String, (BaseTypeValidator, Class[_])]()

    var errors = new JsonObject()

    /**
     * Add validation rule to a query parameter
    */
    def addQueryParam(fieldName: String, rule: BaseTypeValidator): this.type = {
        queryParamRules += (fieldName -> rule)
        this
    }

    /**
     * Add validation rule to a field inside JSON body
    */
    def addJsonBodyParam(fieldName: String, rule: BaseTypeValidator,
        fieldType: Class[_]): this.type = {

        jsonBodyRules += (fieldName -> (rule, fieldType))
        this
    }

    def handle(context: RoutingContext)(implicit logger: ScalaLogger) {
        for ((fieldName, rule) <- queryParamRules) {
            var field = context.request.getParam(fieldName)
            try {
                new RuleValidator(field, fieldName, rule)
            } catch {
                case e: Throwable => {
                    logger.error(e.toString)
                    errors.put(fieldName, e.toString)
                }
            }
        }

        try {
            var body = context.getBodyAsJson
            if (body.nonEmpty) validateJsonBody(body.get)
        } catch {
            case e : DecodeException => {
                if (jsonBodyRules.nonEmpty) {
                    logger.error(e.toString)
                    errors.put("DecodeException", e.toString)
                }
            }
            case _ : Throwable =>
        }

        if (!errors.isEmpty) {
            errorResponse(context.response, errors, 400)
            errors.clear
        } else {
            context.next
        }
    }

    /**
     * Iterate over every json body rules and apply validation on them
    */
    def validateJsonBody(body: JsonObject)(implicit logger: ScalaLogger) {
        for ((fieldName, (rule, fieldType)) <- jsonBodyRules) {
            var field = body.getValue(fieldName)
            var fieldValue = if (field == null) None else Some(field)

            try {
                new RuleValidator(fieldValue, fieldName, rule)
            } catch {
                case e: Throwable => {
                    logger.error(e.toString)
                    errors.put(fieldName, e.toString)
                }
            }
        }
    }
}
