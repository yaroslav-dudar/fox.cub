package fox.cub.math

import scala.math
import scala.collection.mutable.Buffer

object helpers {
    // minimum Mean value
    val minMean = 0.5F
    // minimum dataset size for adjustedMean
    val minSize = 5
    /**
     * Calculate Discrete random variable
    */
    def discreteVariance(data: Seq[Double]): Double = {
        val X = data.distinct
        X.map(x => {
            val p = data.count(_ == x) / data.length.toDouble
            p * math.pow(x - expectedValue[Double](data), 2)
        }).sum
    }

    /**
     * Calculate the Expectation of Discrete varaibale
    */
    def expectedValue[A](data: Seq[A])(implicit num: Numeric[A]): Float = {
        implicitly[Numeric[A]].toFloat(data.sum[A]) / data.length.toFloat
    }

    /**
     * Remove extreme outliers from a dataset and calculate mean
     * Extreme outliers - Max value and Min value
     * If dataset size < minSize don't remove data
     */
    def adjustedMean(data: Buffer[Double]): Float = {
        if (data.size >= minSize) {
            data -= (data.max, data.min)
        }
        math.max(expectedValue(data), minMean)
    }
}
