package fox.cub.model

import scala.collection.mutable.Buffer

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.{JsonObject, JsonArray}

import fox.cub.internals.QueryEvent
import fox.cub.utils.Utils.getUTCdate

object Odds {
    private val Collection = "odds"

    /**
     * Get odds timeline for fixture
     * @param fixtureIds External fixture ids
    */

    def get(fixtureIds: Buffer[Int]): QueryEvent = {
        val filter = Json.obj(("fixture_id",
                               Json.obj(("$in", fixtureIds))))

        val query = new JsonObject()
            .put("find", Collection)
            .put("filter", filter)
            .put("batchSize", 250)

        QueryEvent("find", query)
    }

    def getDiff(fixtureIds: Buffer[Int]): QueryEvent = {
        val filter = Json.obj(("fixture_id",
                               Json.obj(("$in", fixtureIds))))

        val aggMatch = Json.obj(("$match", filter))
        val aggSort = Json.obj(("$sort", Json.obj( ("date", 1) )))

        val group = Json.obj(
            ("$group", Json.obj(
                ("_id", null),
                ("open", Json.obj( ("$first", "$$ROOT") )),
                ("close", Json.obj( ("$last", "$$ROOT") ))
            )))

        val openTotal = Json.obj( ("$arrayElemAt", Json.arr("$open.totals", 0)) )
        val closeTotal = Json.obj( ("$arrayElemAt", Json.arr("$close.totals", 0)) )
        val project_1 = Json.obj(
            ("$project", Json.obj(
                ("open", 1),
                ("close", 1),
                ("openTotal", openTotal),
                ("closeTotal", closeTotal)
            )))


        val project_2 = projectDiff(false)
        var cursor = Json.obj()

        var pipeline = Json.arr(aggMatch, aggSort, group, project_1, project_2)
        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }

    def cond(ifExpr: String, resExpr: JsonObject) = {
        val eq = Json.obj( ("$eq", Json.arr(ifExpr, 0)))
        Json.obj( ("$cond", Json.arr(eq, 1, resExpr)) )
    }

    def divide(fisrt: String, second: String) = Json.obj(("$divide", Json.arr(fisrt, second)))

    def projectDiff(liteOutput: Boolean) = {
        val homeDiff = divide("$open.moneyline.home", "$close.moneyline.home")
        val awayDiff = divide("$open.moneyline.away", "$close.moneyline.away")
        val drawDiff = divide("$open.moneyline.draw", "$close.moneyline.draw")

        var baseProject = Json.obj(
            ("$project", Json.obj(
                ("away_name", 1),
                ("home_name", 1),
                ("homeDiff", cond("$close.moneyline.home", homeDiff)),
                ("awayDiff", cond("$close.moneyline.away", awayDiff)),
                ("drawDiff", cond("$close.moneyline.draw", drawDiff)),
                ("homeWin", "$close.moneyline.home"),
                ("awayWin", "$close.moneyline.away"),
                ("draw", "$close.moneyline.draw")
            )))

        if (!liteOutput)
            baseProject.getJsonObject("$project")
                .put("_id", 1)
                .put("tournament_name", 1)
                .put("external_ids", 1)
                .put("tournament_id", 1)
                .put("date", 1)
                .put("home_id", 1)
                .put("away_id", 1)

        baseProject
    }
}
