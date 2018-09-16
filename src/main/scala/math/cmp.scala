package fox.cub.math

import scala.math

/**
 * Conway–Maxwell–Poisson distribution utils
*/
class CMP {
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
}
