import os
import pandas as pd
import matplotlib.pyplot as plt

# Using test data for now
base_dir = os.path.dirname(__file__)
path = os.path.abspath(os.path.join(base_dir, "..", "TestingData"))

workout_details = pd.read_csv(os.path.join(path, "workout_entries.csv"))
workouts = pd.read_csv(os.path.join(path, "workouts.csv"))
exercises = pd.read_csv(os.path.join(path, "exercises.csv"))

# Merge in Timestamp
if "WorkoutID" in workout_details.columns and "WorkoutID" in workouts.columns:
    workouts["Timestamp"] =  pd.to_datetime(workouts["Timestamp"])
    workout_details = workout_details.merge(
        workouts[["WorkoutID", "Timestamp"]],
        on="WorkoutID",
        how="left"
    )
else:
    workout_details["Timestamp"] = pd.NaT # Fall back to avoid crashing

# Merge in exercise names
if "ExerciseID" in workout_details.columns and "ExerciseID" in exercises.columns:
    workout_details = workout_details.merge(
        exercises[["ExerciseID", "Name"]],
        on="ExerciseID",
        how="left"
    )

# Most popular exercise
exercise_counts = workout_details["Name"].value_counts().reset_index()
exercise_counts.columns = ["Name", "Count"]
print(exercise_counts)

# Bar Chart of most popular exercises
def most_popular_exercise_plot():
    counts = workout_details["Name"].value_counts().reset_index()
    counts.columns = ["Name", "Count"]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(counts["Name"], counts["Count"])
    ax.set_title("Most Popular Exercises")
    ax.set_xlabel("Sets Performed")
    ax.set_ylabel("Exercise")
    plt.tight_layout()
    return fig

# Max weight per exercise
max_weight = workout_details.groupby("Name")["Weight"].max().sort_values(ascending=False).reset_index()
max_weight.columns = ["Name", "Max Weight"]
print(max_weight)

# Bar chart of max weight per exercise
def max_weight_plot():
    max_wt = workout_details.groupby("Name")["Weight"].max().sort_values(
        ascending=True).reset_index()  # ascending=True for best appearance in horizontal bar

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(max_wt["Name"], max_wt["Weight"])
    ax.set_title("Max Weight per Exercise")
    ax.set_xlabel("Weight")
    ax.set_ylabel("Exercise")
    plt.tight_layout()
    return fig
# Progress per exercise
workout_details.Timestamp = pd.to_datetime(workout_details["Timestamp"]) # Convert Timestamp to datetime
workout_details = workout_details.sort_values("Timestamp") # Sort by timestamp

overall_progress = workout_details.groupby("Name")["Weight"].agg(['first', 'last']) # Get first and last exercises weigths
overall_progress["Progress"] = overall_progress["last"] - overall_progress["first"] # Calculate progress
progress_sorted = overall_progress.sort_values(by="Progress", ascending=False)
print(progress_sorted)

progress = workout_details.groupby([workout_details.Timestamp.dt.date, "Name"])["Weight"].max().reset_index() # group by date and exercise, get max weight per day
print(progress)


# Plot progress for selected exercise
def progress_plot(exercise_name):
    if "Timestamp" not in workout_details.columns:
        raise ValueError("Timestamp column missing from merged data")

    progress = workout_details[workout_details["Name"] == exercise_name].copy()
    progress = progress.dropna(subset=["Timestamp"])
    progress = progress.sort_values("Timestamp")

    if progress.empty:
        raise ValueError(f"No data found for exercise: {exercise_name}")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(progress["Timestamp"], progress["Weight"], marker='x')
    ax.set_title(f"Progress for {exercise_name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Max Weight")
    plt.xticks(rotation=90)
    plt.tight_layout()
    return fig

def get_exercise_names():
    return sorted(workout_details["Name"].dropna().unique())
