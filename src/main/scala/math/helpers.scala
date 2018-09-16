package fox.cub.math

import scala.math

object helpers {

    /**
     * Calculate Discrete random variable
    */
    def discreteVariance(data: Seq[Int]): Double = {
        val X = data.distinct
        X.map(x => {
            val p = data.count(_ == x) / data.length.toDouble
            p * math.pow(x - expectedValue(data), 2)
        }).sum
    }

    /**
     * Calculate the Expectation of Discrete varaibale
    */
    def expectedValue(data: Seq[Int]): Double = {
        data.sum / data.length.toDouble
    }
}
