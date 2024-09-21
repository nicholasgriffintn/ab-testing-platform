import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class BayesianABTest:
    """
    Bayesian A/B Testing using PyMC.

    Example usage:

    ab_test = BayesianABTest(prior_successes=30, prior_trials=100)
    ab_test.run_experiment(variant_a_successes=40, variant_a_trials=100,
                        variant_b_successes=50, variant_b_trials=100,
                        uplift_method='percent', num_samples=2000)

    Parameters
    ----------
    prior_successes : int
        Number of successful samples from prior data.

    prior_trials : int
        Number of total trials from prior data.
    """

    def __init__(self, prior_successes, prior_trials):
        self.prior_successes = prior_successes
        self.prior_trials = prior_trials
        self.prior_failures = prior_trials - prior_successes

    def run_experiment(
        self,
        variant_a_successes,
        variant_a_trials,
        variant_b_successes,
        variant_b_trials,
        uplift_method="percent",
        num_samples=2000,
    ):
        """
        Run Bayesian A/B test experiment and calculate uplift.

        Parameters
        ----------
        variant_a_successes : int
            Number of successful samples for variant A (control group).

        variant_a_trials : int
            Number of total trials for variant A.

        variant_b_successes : int
            Number of successful samples for variant B (treatment group).

        variant_b_trials : int
            Number of total trials for variant B.

        uplift_method : str, default='percent'
            Method for calculating uplift ('percent', 'ratio', or 'difference').

        num_samples : int, default=2000
            Number of posterior samples.
        """

        # Defining the Bayesian model using PyMC
        with pm.Model() as model:
            # Priors for variant A and B (Beta distributions with prior data)
            prior_a = pm.Beta(
                "prior_a", alpha=self.prior_successes + 1, beta=self.prior_failures + 1
            )
            prior_b = pm.Beta(
                "prior_b", alpha=self.prior_successes + 1, beta=self.prior_failures + 1
            )

            # Likelihoods (Binomial distributions) based on observed data for each variant
            likelihood_a = pm.Binomial(
                "likelihood_a",
                n=variant_a_trials,
                p=prior_a,
                observed=variant_a_successes,
            )
            likelihood_b = pm.Binomial(
                "likelihood_b",
                n=variant_b_trials,
                p=prior_b,
                observed=variant_b_successes,
            )

            # Sample from the posterior distribution
            trace = pm.sample(num_samples, return_inferencedata=True)

        # Calculate the uplift based on the chosen method
        self.uplift_method = uplift_method
        self.uplift_dist = self._calculate_uplift(trace)

        # Display the results
        self.display_results(trace)

    def _calculate_uplift(self, trace):
        """Calculate the uplift distribution based on the selected method."""
        posterior_a = trace.posterior["prior_a"].values.flatten()
        posterior_b = trace.posterior["prior_b"].values.flatten()

        if self.uplift_method == "percent":
            uplift_dist = (posterior_b - posterior_a) / posterior_a
        elif self.uplift_method == "ratio":
            uplift_dist = posterior_b / posterior_a
        elif self.uplift_method == "difference":
            uplift_dist = posterior_b - posterior_a
        else:
            raise ValueError(
                f"Invalid uplift method: {self.uplift_method}. Use 'percent', 'ratio', or 'difference'."
            )

        return uplift_dist

    def plot_uplift_distribution(self, figsize=(18, 6)):
        """Plot the uplift distribution and cumulative distribution."""
        sns.set_style("whitegrid")
        plt.figure(figsize=figsize)

        # Uplift distribution
        plt.subplot(1, 2, 1)
        plt.title("Uplift Distribution")
        ax = sns.kdeplot(self.uplift_dist, fill=True, color="black")

        if ax.lines:
            kde_x, kde_y = ax.lines[0].get_data()
            cutoff = 1 if self.uplift_method == "ratio" else 0

            plt.axvline(x=cutoff, linestyle="--", color="black")
            plt.fill_between(
                kde_x, kde_y, where=(kde_x <= cutoff), color="orange", alpha=0.6
            )
            plt.fill_between(
                kde_x, kde_y, where=(kde_x > cutoff), color="lightgreen", alpha=0.6
            )

        plt.xlabel("Uplift")
        plt.ylabel("Density")

        # Cumulative distribution
        plt.subplot(1, 2, 2)
        plt.title("Cumulative Uplift Distribution")
        sns.kdeplot(self.uplift_dist, cumulative=True, color="blue", fill=True)
        plt.xlabel("Cumulative Uplift")
        plt.ylabel("Density")

        plt.show()

    def display_results(self, trace):
        """Display the results of the Bayesian A/B test."""
        uplift_percent_above_0 = np.mean(self.uplift_dist >= 0)

        # Print summary of results
        print("\nBayesian A/B Test Summary\n==========================")
        print(f"Evaluation Metric: {self.uplift_method.capitalize()} Uplift")
        print(
            f"Uplift above threshold: {uplift_percent_above_0 * 100:.2f}% of simulations\n"
        )

        # Plot the posterior distributions and uplift
        self.plot_uplift_distribution()

        # Use ArviZ to summarize the posterior distributions
        print("\nPosterior Distributions\n=======================")
        az.summary(trace)
        az.plot_posterior(trace)
        plt.show()
