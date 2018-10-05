package fox.cub.betting

import scala.collection.mutable.ArrayBuffer

class BettingEvents(home: ArrayBuffer[Double], away: ArrayBuffer[Double]) {

    val home_2_5 = List(2, 1, 0, 0, 1, 0)
    val away_2_5 = List(0, 1, 2, 0, 0, 1)

    val home_3_5 = home_2_5 ++ List(3, 0, 2, 1)
    val away_3_5 = away_2_5 ++ List(0, 3, 1, 2)

    def _2_5() = {
        var under = 0.0
        for (i <- 0 to home_2_5.size -1) {
            under += home(home_2_5(i)) * away(away_2_5(i))
        }
        val over = 1 - under
        (under, over)
    }

    def _3_5() = {
        var under = 0.0
        for (i <- 0 to home_3_5.size -1) {
            under += home(home_3_5(i)) * away(away_3_5(i))
        }
        val over = 1 - under
        (under, over)
    }

    def draw() = {
        (0 to home.size - 1).toList.map(goals => home(goals) * away(goals)).sum
    }

    def homeWin() = {
        var chance = 0.0

        for (homeGoals <- 0 to home.size -1) {
            for (awayGoals <- 0 to away.size -1) {
                if (homeGoals > awayGoals)
                    chance += home(homeGoals) * away(awayGoals)
            }
        }

        chance
    }

    def awayWin() = {
        var chance = 0.0

        for (homeGoals <- 0 to home.size -1) {
            for (awayGoals <- 0 to away.size -1) {
                if (homeGoals < awayGoals)
                    chance += home(homeGoals) * away(awayGoals)
            }
        }

        chance
    }

    def btts() = {
        var homeTeamScore = 1 - home(0)
        var awayTeamScore = 1 - away(0)

        homeTeamScore * awayTeamScore
    }
}
