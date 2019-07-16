package fox.cub.betting

import scala.collection.mutable.ArrayBuffer
import scala.math

/**
 * @param scoreline array with moneyline probabilities.
 * Where index
 * 0: draw
 * 1: home win by 1 goal
 * 2: home win by 2 goals
 * 3: home win by more then 2 goals
 * 4: away win by 1 goal
 * 5: away win by 2 goals
 * 6: away win by more then 2 goals
 * @param total array of amount of goals probabilities.
 * Where index equal to amount of goals
*/
class BettingEvents(scoreline: ArrayBuffer[Double],
    total: ArrayBuffer[Double], btts: ArrayBuffer[Double]) {

    def _1_5() = {
        var under = total.take(2).sum
        val over = 1 - under
        (under, over)
    }

    def _2_5() = {
        var under = total.take(3).sum
        val over = 1 - under
        (under, over)
    }

    def _3_5() = {
        var under = total.take(4).sum
        val over = 1 - under
        (under, over)
    }

    def draw() = scoreline(0)

    def homeWin() = scoreline.slice(1,4).sum

    def awayWin() = scoreline.slice(4,7).sum

    def home_1_5() = scoreline.slice(2,4).sum

    def home_2_5() = scoreline(3)

    def away_1_5 = scoreline.slice(5,7).sum

    def home_0(home: Double, away: Double) = 100/(home + away) * home

    def away_2_5 = scoreline(6)

    def away_0(home: Double, away: Double) = 100/(home + away) * away

    def getEventsList() = {
        val _home = homeWin
        val _away = awayWin
        val _draw = draw

        List(("under 1.5", _1_5._1),
             ("over 1.5", _1_5._2),
             ("under 2.5", _2_5._1),
             ("over 2.5", _2_5._2),
             ("under 3.5", _3_5._1),
             ("over 3.5", _3_5._2),
             ("BTTS", btts.last),
             ("Home Win", _home),
             ("Home Win +1.5", home_1_5),
             ("Home Win +2.5", home_2_5),
             ("Away Win", _away),
             ("Away Win +1.5", away_1_5),
             ("Away Win +2.5", away_2_5),
             ("Draw", _draw),
             ("Home Double Chance", _home + _draw),
             ("Away Double Chance", _away + _draw),
             ("Home Draw No Bet", home_0(_home, _away)),
             ("Away Draw No Bet", away_0(_home, _away)))
    }
}
