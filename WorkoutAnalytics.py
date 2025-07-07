import os
import pandas as pd
import matplotlib.pyplot as plt


# Test data sets
base_dir = os.path.dirname(__file__)
workout_path = os.path.abspath(os.path.join(base_dir, "..", "TestingData"))
workouts = pd.read_csv(os.path.join(workout_path, "workouts.csv"))
workouts["Timestamp"] = pd.to_datetime(workouts["Timestamp"])

# Prepare and information
workouts["Timestamp"] = pd.to_datetime(workouts["Timestamp"]) # convert Timestamp to datetime
print(workouts.head())
print(workouts.info())

# Best time for workouts
all_hours = pd.DataFrame({"Hour": range(24)})
workouts["Change in Mood"] = workouts.PostMood - workouts.PreMood
workouts["Hour"] = workouts["Timestamp"].dt.hour # extract hour of day
hourly_mood_change = workouts.groupby("Hour")["Change in Mood"].mean().reset_index() # Group mood chaneg by hour
full_hourly = pd.merge(all_hours, hourly_mood_change, on="Hour", how="left")
full_hourly["Change in Mood"] = full_hourly["Change in Mood"]
full_hourly = full_hourly.sort_values(by="Change in Mood", ascending=False).reset_index()
print("-------------------------------------")
print(full_hourly)

def mood_change_by_hour_plot():
    workouts["Change in Mood"] = workouts.PostMood - workouts.PreMood
    workouts["Hour"] = workouts["Timestamp"].dt.hour
    hourly = workouts.groupby("Hour")["Change in Mood"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(hourly["Hour"], hourly["Change in Mood"])
    ax.set_title("Average Mood Change per Hour")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Change in Mood")
    plt.tight_layout()
    return fig

# Average mood change from workout
avg_mood_change = workouts["Change in Mood"].mean()
print(avg_mood_change)

