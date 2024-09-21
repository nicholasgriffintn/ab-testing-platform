import hashlib

from .frequentist import FrequentistABTest
from .bayesian import BayesianABTest


class UserBucketingABTest:
    """
    A/B Testing with User Bucketing for both Frequentist and Bayesian approaches. Designed to be used
    with data already in the data warehouse.

    Example usage:

    user_data = [
        {'user_id': 1, 'event': 1}, {'user_id': 2, 'event': 0}, {'user_id': 3, 'event': 1},
        {'user_id': 4, 'event': 1}, {'user_id': 5, 'event': 0}, {'user_id': 6, 'event': 0},
        # More users...
    ]
    group_buckets = {
        'control': range(0, 50),
        'test1': range(50, 75),
        'test2': range(75, 100)
    }
    ab_test = UserBucketingABTest(method='frequentist', alpha=0.05)
    result = ab_test.run_experiment(user_data, group_buckets)

    Parameters
    ----------
    method : str
        'frequentist' or 'bayesian' to specify which A/B testing method to use.

    alpha : float, default=0.05
        Significance level for Frequentist A/B testing.

    prior_successes : int, optional
        Number of prior successes for Bayesian A/B testing.

    prior_trials : int, optional
        Number of prior trials for Bayesian A/B testing.

    num_samples : int, optional
        Number of posterior samples for Bayesian A/B testing.
    """

    def __init__(
        self, method, alpha=0.05, prior_successes=30, prior_trials=100, num_samples=2000
    ):
        self.method = method
        self.alpha = alpha
        self.prior_successes = prior_successes
        self.prior_trials = prior_trials
        self.num_samples = num_samples

    def bucket_user(self, user_id, bucket_count=100):
        """
        Assign a user to a bucket based on a hashed value of their user_id.

        Parameters
        ----------
        user_id : str or int
            The unique identifier for a user.

        bucket_count : int, default=100
            The total number of buckets (this determines the granularity of bucketing).

        Returns
        -------
        int
            A bucket number between 0 and bucket_count-1.
        """
        hashed_value = int(hashlib.sha256(str(user_id).encode("utf-8")).hexdigest(), 16)
        return hashed_value % bucket_count

    def assign_to_group(self, user_id, group_buckets):
        """
        Assign a user to a group based on their bucket.

        Parameters
        ----------
        user_id : str or int
            The unique identifier for a user.

        group_buckets : dict
            A dictionary where keys are group names and values are ranges of buckets assigned to each group.

        Returns
        -------
        str
            The group name based on the user's bucket assignment.
        """
        user_bucket = self.bucket_user(user_id)
        for group, bucket_range in group_buckets.items():
            if user_bucket in bucket_range:
                return group
        raise ValueError("User not assigned to a valid group.")

    def run_experiment(self, user_data, group_buckets):
        """
        Run the A/B test experiment on the given user data.

        Parameters
        ----------
        user_data : list of dicts
            A list of dictionaries where each dictionary represents a user and contains the following keys:
            - 'user_id': The unique identifier for the user.
            - 'event': 1 for success (e.g., clicked), 0 for failure (e.g., did not click).

        group_buckets : dict
            A dictionary where keys are group names and values are ranges of buckets assigned to each group.

        Returns
        -------
        dict
            A dictionary containing the test results (statistic, p-value, or uplift distribution).
        """
        group_results = {
            group: {"success": 0, "trials": 0} for group in group_buckets.keys()
        }

        # Assign users to groups and record their results
        for user in user_data:
            group = self.assign_to_group(user["user_id"], group_buckets)
            group_results[group]["trials"] += 1
            group_results[group]["success"] += user["event"]

        if self.method == "frequentist":
            return self.run_frequentist_test(group_results)
        elif self.method == "bayesian":
            return self.run_bayesian_test(group_results)
        else:
            raise ValueError(f"Unknown method: {self.method}")

    def run_frequentist_test(self, group_results):
        """
        Run Frequentist A/B testing.

        Parameters
        ----------
        group_results : dict
            A dictionary with group names as keys and dictionaries with 'success' and 'trials' as values.

        Returns
        -------
        dict
            A dictionary with the test statistic and p-value.
        """
        control_group = "control"
        test_groups = [
            group for group in group_results.keys() if group != control_group
        ]

        results = {}
        for test_group in test_groups:
            control_success = group_results[control_group]["success"]
            control_trials = group_results[control_group]["trials"]
            test_success = group_results[test_group]["success"]
            test_trials = group_results[test_group]["trials"]

            exp = FrequentistABTest(alpha=self.alpha, alt_hypothesis="two_tailed")
            stat, pvalue = exp.conduct_experiment(
                control_success, control_trials, test_success, test_trials
            )

            results[test_group] = {
                "method": "frequentist",
                "statistic": stat,
                "p_value": pvalue,
                "control_success": control_success,
                "control_trials": control_trials,
                "test_success": test_success,
                "test_trials": test_trials,
            }

        return results

    def run_bayesian_test(self, group_results):
        """
        Run Bayesian A/B testing.

        Parameters
        ----------
        group_results : dict
            A dictionary with group names as keys and dictionaries with 'success' and 'trials' as values.

        Returns
        -------
        dict
            A dictionary with the uplift distribution.
        """
        control_group = "control"
        test_groups = [
            group for group in group_results.keys() if group != control_group
        ]

        results = {}
        for test_group in test_groups:
            control_success = group_results[control_group]["success"]
            control_trials = group_results[control_group]["trials"]
            test_success = group_results[test_group]["success"]
            test_trials = group_results[test_group]["trials"]

            exp = BayesianABTest(self.prior_successes, self.prior_trials)
            exp.run_experiment(
                control_success,
                control_trials,
                test_success,
                test_trials,
                uplift_method="percent",
                num_samples=self.num_samples,
            )

            results[test_group] = {
                "method": "bayesian",
                "control_success": control_success,
                "control_trials": control_trials,
                "test_success": test_success,
                "test_trials": test_trials,
            }

        return results
