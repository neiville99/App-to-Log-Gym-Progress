import os
import pandas as pd
import matplotlib.pyplot as plt
from pandas import to_datetime

base_dir = os.path.dirname(__file__)
file_path = os.path.abspath(os.path.join(base_dir, "..", "TestingData", "weightlog.csv"))
weights = pd.read_csv(file_path)

# Overview of dataset
print(weights.head())
print(weights.info())
weight_range = weights.WeightKg.max() - weights.WeightKg.min()
print("The range of weight values: ", weight_range)

# Preperation
weights.Timestamp = to_datetime(weights['Timestamp'])

# Create Plot
def create_weight_plot():
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(weights['Timestamp'], weights['WeightKg'])
    ax.set_title("Weight over time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Weight (kg)")
    fig.autofmt_xdate(rotation=90)
    plt.tight_layout()
    plt.show()

    return fig

create_weight_plot()
