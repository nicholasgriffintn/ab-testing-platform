import matplotlib.pyplot as plt


def plot_power_curve(effect_sizes, powers, observed_effect_size):
    """Plot the power curve for the given effect sizes and powers."""
    plt.figure(figsize=(10, 6))
    plt.plot(effect_sizes, powers, label="Power Curve")
    plt.axhline(y=0.8, color="red", linestyle="--", label="80% Power Threshold")
    plt.axvline(
        x=observed_effect_size,
        color="blue",
        linestyle="--",
        label="Observed Effect Size",
    )
    plt.title("Power Curve for A/B Test")
    plt.xlabel("Effect Size (Difference in Proportions)")
    plt.ylabel("Power")
    plt.legend()
    plt.show()
