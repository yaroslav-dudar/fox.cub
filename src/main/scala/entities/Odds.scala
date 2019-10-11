package fox.cub.model

import scala.collection.mutable.Buffer

import io.vertx.lang.scala.json.Json
import io.vertx.core.json.JsonObject
import io.vertx.core.json.JsonArray

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
                ("openLine", Json.obj( ("$first", "$$ROOT") )),
                ("closingLine", Json.obj( ("$last", "$$ROOT") ))
            )))

        val openTotal = Json.obj( ("$arrayElemAt", Json.arr("$openLine.totals", 0)) )
        val closingTotal = Json.obj( ("$arrayElemAt", Json.arr("$closingLine.totals", 0)) )
        val project_1 = Json.obj(
            ("$project", Json.obj(
                ("openLine", 1),
                ("closingLine", 1),
                ("openTotal", openTotal),
                ("closingTotal", closingTotal)
            )))

        val homeDiff = Json.obj(("$subtract", Json.arr("$closingLine.moneyline.home",
                                                       "$openLine.moneyline.home")))
        val awayDiff = Json.obj(("$subtract", Json.arr("$closingLine.moneyline.away",
                                                       "$openLine.moneyline.away")))
        val drawDiff = Json.obj(("$subtract", Json.arr("$closingLine.moneyline.draw",
                                                       "$openLine.moneyline.draw")))
        val totalPointsDiff = Json.obj(("$subtract", Json.arr("$closingTotal.points",
                                                              "$openTotal.points")))
        val totalOverDiff = Json.obj(("$subtract", Json.arr("$closingTotal.over",
                                                            "$openTotal.over")))
        val totalUnderDiff = Json.obj(("$subtract", Json.arr("$closingTotal.under",
                                                             "$openTotal.under")))
        val project_2 = Json.obj(
            ("$project", Json.obj(
                ("_id", 0),
                ("homeDiff", homeDiff),
                ("awayDiff", awayDiff),
                ("drawDiff", drawDiff),
                ("totalPointsDiff", totalPointsDiff),
                ("totalOverDiff", totalOverDiff),
                ("totalUnderDiff", totalUnderDiff)
            )))

        var cursor = Json.obj()

        var pipeline = Json.arr(aggMatch, aggSort, group, project_1, project_2)
        val query = new JsonObject().put("aggregate", Collection).
            put("pipeline", pipeline).put("cursor", cursor)

        QueryEvent("aggregate", query)
    }
}
