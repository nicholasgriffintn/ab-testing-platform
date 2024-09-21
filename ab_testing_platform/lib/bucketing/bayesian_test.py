from ..bayesian import BayesianABTest


def run_bayesian_test(group_results, prior_successes, prior_trials, num_samples):
    """
    Run Bayesian A/B testing.

    Parameters
    ----------
    group_results : dict
        A dictionary with group names as keys and dictionaries with 'success' and 'trials' as values.

    prior_successes : int
        Number of prior successes for Bayesian A/B testing.

    prior_trials : int
        Number of prior trials for Bayesian A/B testing.

    num_samples : int
        Number of posterior samples for Bayesian A/B testing.

    Returns
    -------
    dict
        A dictionary with the uplift distribution.
    """
    control_group = "control"
    test_groups = [group for group in group_results.keys() if group != control_group]

    results = {}
    for test_group in test_groups:
        control_success = group_results[control_group]["success"]
        control_trials = group_results[control_group]["trials"]
        test_success = group_results[test_group]["success"]
        test_trials = group_results[test_group]["trials"]

        exp = BayesianABTest(prior_successes, prior_trials)
        exp.run_experiment(
            control_success,
            control_trials,
            test_success,
            test_trials,
            uplift_method="percent",
            num_samples=num_samples,
        )

        results[test_group] = {
            "method": "bayesian",
            "control_success": control_success,
            "control_trials": control_trials,
            "test_success": test_success,
            "test_trials": test_trials,
        }

    return results
