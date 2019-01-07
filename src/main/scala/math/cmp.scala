package fox.cub.math

import scala.math
import scala.collection.mutable.ArrayBuffer

/**
 * Conway–Maxwell–Poisson distribution utils
*/
object CMP {

    /**
     * @param mu location parameter (e.g Expected value)
     * @param nu shape parameter
     * @param x value for each probability calculated
    */
    def dist(mu: Double, nu: Double, x: Int): Double = {
        val norm = Z(mu, nu)
        val logLike = nu * x * math.log(mu) - nu * math.log(factorial(x)) - norm
        math.exp(logLike)
    }

    /**
     * Calculate normalizing constant
    */
    def Z(mu: Double, nu: Double): Double = {
        val expression1 = nu * mu
        val expression2 = ((nu-1)/(2)) * math.log(mu)
        val expression3 = ((nu-1)/2) * math.log(2*math.Pi)
        val expression4 = 0.5 * math.log(nu)

        expression1 - expression2 - expression3 - expression4
    }


    /**
     * Calculate factorial function <number!>
    */
    @annotation.tailrec
    final def factorial(number: Int, result: Int = 1): Int = {
        if (number == 0)
            result
        else
            factorial(number -1, result * number)
    }

    def distRange(mu: Double, nu: Double, max: Int = 5): ArrayBuffer[Double] = {
        var dists = ArrayBuffer[Double]()
        for( x <- 0 to max) {
            dists += dist(mu, nu, x)
        }
        dists
    }

    /**
     * Calculate distribution in range [0 - max]
     * Split [max - Inf] probabilities within [0 - max]
     * @return probability distribution within [0 - max] range
    */
    def adjustedDistRange(mu: Double, nu: Double, max: Int = 5): ArrayBuffer[Double] = {

        var thresholdLow = 0.035
        var thresholdHigh = 0.07

        var range = distRange(mu, nu, max)
        var probLeft = 1 - range.sum
        var dists = ArrayBuffer[Double]()
        var coefs: List[Double] = null // should be 1 in total

        if (probLeft > thresholdLow && probLeft < thresholdHigh) {
            // update all probs uniformly
            coefs = (0 to max).toList.map(_ => 1 / (max + 1).toDouble)
        } else if (probLeft > thresholdHigh) {
            // update all probs, but high outcomes should have an advantage
            val coef_avg = 0.8 / (max - 2)
            coefs = List(0.1, 0.1) ++ (2 to max).toList.map(_ => coef_avg)
        } else {
            // update only 0, 1 probs
            coefs = List(0.5, 0.5) ++ (2 to max).toList.map(_ => 0.0)
        }

        for( x <- 0 to max) {
            dists += range(x) + coefs(x) * probLeft
        }
        dists
    }

    /**
     * Calculate nu param based on input observations
     * @param observs list of discrete random variables
     */
    def getShapeParam(observs: Seq[Double]): Double = {
        var overdispersionMax = 0.5
        var underdispersionMax = 1.25
        // normal dispersion by default
        var defaultShape = 1.0

        var variance = helpers.discreteVariance(observs)
        var expVal = helpers.expectedValue(observs)

        var variabilityDiff = variance - expVal
        if (variabilityDiff < 0) {
            // underdispersion
            var extraShape = math.abs(variabilityDiff) / expVal * (underdispersionMax - defaultShape)
            return extraShape + defaultShape
        } else if (variabilityDiff > 0) {
            // overdispersion
            var extraShape = math.abs(variabilityDiff) / expVal * (defaultShape - overdispersionMax)
            return defaultShape - math.min(extraShape, defaultShape - overdispersionMax)
        }

        return defaultShape
    }
}
