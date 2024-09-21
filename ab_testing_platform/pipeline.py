import click

from .lib.bucketing import UserBucketingABTest


def run_experiment(user_data, group_buckets):
    """
    Run an A/B test based on the provided user data.
    """
    method = click.prompt("Choose testing method: 'frequentist' or 'bayesian'")

    if method not in ["frequentist", "bayesian"]:
        click.echo(
            "Invalid method. Please choose either 'frequentist' or 'bayesian'.",
            err=True,
        )
        return

    if method == "frequentist":
        alpha = click.prompt(
            "Enter alpha (significance level)", type=float, default=0.05
        )
        ab_test = UserBucketingABTest(method="frequentist", alpha=alpha)
    else:
        prior_successes = click.prompt(
            "Enter prior successes for Bayesian", type=int, default=30
        )
        prior_trials = click.prompt(
            "Enter prior trials for Bayesian", type=int, default=100
        )
        ab_test = UserBucketingABTest(
            method="bayesian",
            prior_successes=prior_successes,
            prior_trials=prior_trials,
        )

    result = ab_test.run_experiment(user_data, group_buckets)

    if result is None:
        click.echo("Error running the experiment.", err=True)
        return

    # Show results
    if method == "frequentist":
        for test_group, result in result.items():
            click.echo(f"\nFrequentist Test Results for {test_group}\n{'='*25}")
            click.echo(f"Test Statistic (Z): {result['statistic']:.4f}")
            click.echo(f"P-Value: {result['p_value']:.4f}")
            click.echo(
                f"Control Successes: {result['control_success']} / {result['control_trials']}"
            )
            click.echo(
                f"Test Successes: {result['test_success']} / {result['test_trials']}"
            )
    else:
        print(result)

        {
            "test1": {
                "method": "bayesian",
                "control_success": 1,
                "control_trials": 2,
                "test_success": 1,
                "test_trials": 2,
            }
        }

        for test_group, result in result.items():
            click.echo(f"\nBayesian Test Results for {test_group}\n{'='*25}")
            click.echo(
                f"Control Successes: {result['control_success']} / {result['control_trials']}"
            )
            click.echo(
                f"Test Successes: {result['test_success']} / {result['test_trials']}"
            )
