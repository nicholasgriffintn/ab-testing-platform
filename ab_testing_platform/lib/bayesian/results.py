import numpy as np
import arviz as az
import matplotlib.pyplot as plt

from .plotting import plot_uplift_distribution

def display_results(trace, uplift_dist, uplift_method):
    """Display the results of the Bayesian A/B test."""
    uplift_percent_above_0 = np.mean(uplift_dist >= 0)

    # Print summary of results
    print("\nBayesian A/B Test Summary\n==========================")
    print(f"Evaluation Metric: {uplift_method.capitalize()} Uplift")
    print(
        f"Uplift above threshold: {uplift_percent_above_0 * 100:.2f}% of simulations\n"
    )

    # Plot the posterior distributions and uplift
    plot_uplift_distribution(uplift_dist, uplift_method)

    # Use ArviZ to summarize the posterior distributions
    print("\nPosterior Distributions\n=======================")
    az.summary(trace)
    az.plot_posterior(trace)
    plt.show()