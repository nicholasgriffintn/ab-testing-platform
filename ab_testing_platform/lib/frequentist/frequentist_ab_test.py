import numpy as np
import scipy.stats as st

from .validation import validate_hypothesis
from .calculations import calculate_pvalue, calculate_power
from .plotting import plot_power_curve


class FrequentistABTest:
    """
    Frequentist A/B Testing aka Two sample proportion test.

    Example usage:

    ab_test = FrequentistABTest(alpha=0.05, alt_hypothesis='two_tailed')
    ab_test.conduct_experiment(success_null=300, trials_null=1000, success_alt=350, trials_alt=1000)
    ab_test.plot_power_curve()

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level or Type I error rate.

    alt_hypothesis : str, default='one_tailed'
        Defines the hypothesis test.

        * 'one_tailed': one-tailed hypothesis test.
        * 'two_tailed': two-tailed hypothesis test.
    """

    def __init__(self, alpha=0.05, alt_hypothesis="one_tailed"):
        self.alpha = alpha
        self.alt_hypothesis = alt_hypothesis.lower()
        validate_hypothesis(self.alt_hypothesis, self.alpha)

    def conduct_experiment(
        self,
        success_null,
        trials_null,
        success_alt,
        trials_alt,
        sequential=False,
        stopping_threshold=0.05,
    ):
        """
        Conduct A/B test and calculate the statistical significance.

        Parameters
        ----------
        success_null : int
            Successful trials (Version A).
        trials_null : int
            Total trials for Version A.
        success_alt : int
            Successful trials (Version B).
        trials_alt : int
            Total trials for Version B.
        sequential : bool, default=False
            Whether to perform sequential testing.
        stopping_threshold : float, default=0.05
            P-value threshold for stopping the sequential test

        Returns
        -------
        stat : float
            Z statistic (or t-statistic in small sample cases).
        pvalue : float
            The probability of observing the test statistic as extreme or more extreme than observed.
        """
        self.success_null = success_null
        self.trials_null = trials_null
        self.success_alt = success_alt
        self.trials_alt = trials_alt

        self.prop_null = success_null / trials_null
        self.prop_alt = success_alt / trials_alt

        pooled_prop = (success_null + success_alt) / (trials_null + trials_alt)
        se_pooled = np.sqrt(
            pooled_prop * (1 - pooled_prop) * (1 / trials_null + 1 / trials_alt)
        )

        self.stat = (self.prop_alt - self.prop_null) / se_pooled
        
        print(f"Running {'sequential' if sequential else 'non-sequential'} Frequentist A/B test")

        if sequential:
            for i in range(1, trials_null + trials_alt + 1):
                # Update null and alternative success counts incrementally
                success_null_i = int(i * (success_null / (trials_null + trials_alt)))
                success_alt_i = int(i * (success_alt / (trials_null + trials_alt)))
                
                prop_null_i = success_null_i / i
                prop_alt_i = success_alt_i / i
                
                pooled_prop_i = (success_null_i + success_alt_i) / (2 * i)
                se_pooled_i = np.sqrt(pooled_prop_i * (1 - pooled_prop_i) * (2 / i))

                # Avoid division by zero or very small numbers
                if se_pooled_i == 0:
                    stat_i = np.nan  # Or handle this case appropriately
                else:
                    stat_i = (prop_alt_i - prop_null_i) / se_pooled_i
                pvalue_i = calculate_pvalue(stat_i, self.alt_hypothesis, self.alpha)
                self.pvalue = pvalue_i
                
                if pvalue_i < stopping_threshold:
                    print(f"Stopping early at trial {i} with p-value {pvalue_i:.4f}")
                    break
        else:
            self.pvalue = calculate_pvalue(self.stat, self.alt_hypothesis, self.alpha)

        return self.get_freq_results()

    def get_freq_results(self):
        """Returns the results of the A/B test."""

        plots = self.plot_power_curve()

        results = {
            "version_a": {
                "success": self.success_null,
                "trials": self.trials_null,
                "proportion": self.prop_null,
            },
            "version_b": {
                "success": self.success_alt,
                "trials": self.trials_alt,
                "proportion": self.prop_alt,
            },
            "statistic": self.stat,
            "pvalue": self.pvalue,
            "significant": self.pvalue < self.alpha,
            "plots": plots,
        }
        return results

    def plot_power_curve(self):
        """
        Generate and plot a power curve for the given A/B test parameters.
        This assumes that the null hypothesis is true, and calculates power for a range of alternative hypotheses.
        """
        effect_sizes = np.arange(0, 0.2, 0.005)
        powers = [
            calculate_power(
                self.prop_null,
                self.trials_null,
                self.trials_alt,
                es,
                self.alpha,
                self.alt_hypothesis,
            )
            for es in effect_sizes
        ]

        return plot_power_curve(effect_sizes, powers, self.prop_alt - self.prop_null)
