import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ==============================
# Load Dataset
# ==============================

# Replace with your dataset file name
df = pd.read_csv("dataset-eye_blink_data.csv")

# ==============================
# Basic Information
# ==============================

print(df.head())
print("\nClass Distribution:")
print(df["Class_Label"].value_counts())

# ==============================
# Separate Classes
# ==============================

normal = df[df["Class_Label"] == "Normal"]
fatigue = df[df["Class_Label"] == "Fatigue_Dryness"]

# ==============================
# Scatter Plot Visualization
# ==============================

features = [
    "Blink_Rate",
    "Blink_Duration",
    "Incomplete_Blink_Ratio"
]

for feature in features:

    plt.figure(figsize=(10, 5))

    # X-axis index
    x_normal = np.arange(len(normal))
    x_fatigue = np.arange(len(fatigue))

    # Scatter points
    plt.scatter(
        x_normal,
        normal[feature],
        label="Normal",
        alpha=0.7
    )

    plt.scatter(
        x_fatigue,
        fatigue[feature],
        label="Fatigue_Dryness",
        alpha=0.7
    )

    plt.title(f"Scatter Plot of {feature}")
    plt.xlabel("Sample Index")
    plt.ylabel(feature)
    plt.legend()
    plt.grid(True)

    plt.show()

# ==============================
# Histogram Visualization
# ==============================

for feature in features:

    plt.figure(figsize=(10, 5))

    plt.hist(
        normal[feature],
        bins=30,
        alpha=0.6,
        label="Normal"
    )

    plt.hist(
        fatigue[feature],
        bins=30,
        alpha=0.6,
        label="Fatigue_Dryness"
    )

    plt.title(f"Histogram of {feature}")
    plt.xlabel(feature)
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)

    plt.show()

# ==============================
# Distribution Curves
# ==============================

for feature in features:

    plt.figure(figsize=(10, 5))

    # Normal class
    normal_values = normal[feature]
    fatigue_values = fatigue[feature]

    # Histogram density
    plt.hist(
        normal_values,
        bins=30,
        density=True,
        alpha=0.5,
        label="Normal"
    )

    plt.hist(
        fatigue_values,
        bins=30,
        density=True,
        alpha=0.5,
        label="Fatigue_Dryness"
    )

    # Gaussian curve for Normal class
    mu_n = normal_values.mean()
    sigma_n = normal_values.std()

    x_n = np.linspace(normal_values.min(), normal_values.max(), 200)

    y_n = (
        1 / (sigma_n * np.sqrt(2 * np.pi))
    ) * np.exp(
        -0.5 * ((x_n - mu_n) / sigma_n) ** 2
    )

    plt.plot(x_n, y_n, linewidth=2)

    # Gaussian curve for Fatigue class
    mu_f = fatigue_values.mean()
    sigma_f = fatigue_values.std()

    x_f = np.linspace(fatigue_values.min(), fatigue_values.max(), 200)

    y_f = (
        1 / (sigma_f * np.sqrt(2 * np.pi))
    ) * np.exp(
        -0.5 * ((x_f - mu_f) / sigma_f) ** 2
    )

    plt.plot(x_f, y_f, linewidth=2)

    plt.title(f"Gaussian Distribution of {feature}")
    plt.xlabel(feature)
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True)

    plt.show()