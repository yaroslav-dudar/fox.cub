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
    total: ArrayBuffer[Double]) {

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

    def away_2_5 = scoreline(6)
}
