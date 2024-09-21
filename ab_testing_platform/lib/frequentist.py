import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt


class FrequentistABTest:
    """
    Frequentist A/B Testing aka Two sample proportion test.

    Example usgae:

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
        self.validate_hypothesis()

    def validate_hypothesis(self):
        """Validate the hypothesis input and alpha level."""
        valid_hypotheses = ["one_tailed", "two_tailed"]
        if self.alt_hypothesis not in valid_hypotheses:
            raise ValueError(
                f"Invalid hypothesis type: {self.alt_hypothesis}. Choose from {valid_hypotheses}."
            )
        if not (0 < self.alpha < 1):
            raise ValueError(f"Alpha should be between 0 and 1, but got {self.alpha}.")

    def conduct_experiment(self, success_null, trials_null, success_alt, trials_alt):
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

        self.pvalue = self.calculate_pvalue()
        self.print_freq_results()

        return self.stat, self.pvalue

    def calculate_pvalue(self):
        """Calculate the p-value based on the test statistic and the hypothesis type."""
        if self.alt_hypothesis == "one_tailed":
            return (
                1 - st.norm.cdf(np.abs(self.stat))
                if self.stat > 0
                else st.norm.cdf(self.stat)
            )
        elif self.alt_hypothesis == "two_tailed":
            return 2 * (1 - st.norm.cdf(np.abs(self.stat)))

    def print_freq_results(self):
        """Prints the results of the A/B test."""
        print("\nFrequentist A/B Test Summary\n============================")
        print(
            f"Version A: {self.success_null}/{self.trials_null} ({self.prop_null:.2%})"
        )
        print(f"Version B: {self.success_alt}/{self.trials_alt} ({self.prop_alt:.2%})")
        print(f"Test Statistic (Z): {self.stat:.4f}")
        print(f"P-Value: {self.pvalue:.4f}")
        print(
            f"Significant at alpha={self.alpha}? {'Yes' if self.pvalue < self.alpha else 'No'}"
        )

    def plot_power_curve(self):
        """
        Generate and plot a power curve for the given A/B test parameters.
        This assumes that the null hypothesis is true, and calculates power for a range of alternative hypotheses.
        """
        effect_sizes = np.arange(0, 0.2, 0.005)
        powers = [self.calculate_power(es) for es in effect_sizes]

        plt.figure(figsize=(10, 6))
        plt.plot(effect_sizes, powers, label="Power Curve")
        plt.axhline(y=0.8, color="red", linestyle="--", label="80% Power Threshold")
        plt.axvline(
            x=self.prop_alt - self.prop_null,
            color="blue",
            linestyle="--",
            label="Observed Effect Size",
        )
        plt.title("Power Curve for A/B Test")
        plt.xlabel("Effect Size (Difference in Proportions)")
        plt.ylabel("Power")
        plt.legend()
        plt.show()

    def calculate_power(self, effect_size):
        """Calculate the power of the test given a specific effect size."""
        se_pooled = np.sqrt(
            self.prop_null
            * (1 - self.prop_null)
            * (1 / self.trials_null + 1 / self.trials_alt)
        )
        z_alpha = (
            st.norm.ppf(1 - self.alpha / 2)
            if self.alt_hypothesis == "two_tailed"
            else st.norm.ppf(1 - self.alpha)
        )
        z_effect = effect_size / se_pooled
        return 1 - st.norm.cdf(z_alpha - z_effect)
