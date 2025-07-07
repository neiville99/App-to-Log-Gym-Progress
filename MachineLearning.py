import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load data
exercises = pd.read_csv("../TestingData/exercises.csv")
entries = pd.read_csv("../TestingData/workout_entries.csv")
workouts = pd.read_csv("../TestingData/workouts.csv")

# Merge entries with exercises to get Name
entries = pd.merge(entries, exercises[["ExerciseID", "Name"]], on="ExerciseID", how="left")

# Merge with workouts to get workout context
data = pd.merge(entries, workouts, on="WorkoutID")
data["Timestamp"] = pd.to_datetime(data["Timestamp"])
data = data.sort_values("Timestamp")

# Filter by specific exercise
exercise_name = input("Which exercise would you like to predict? ")
exercise_data = data[data["Name"] == exercise_name].copy()

# Create X and y
exercise_data["DayNumber"] = (exercise_data["Timestamp"] - exercise_data["Timestamp"].min()).dt.days
X = exercise_data[["DayNumber"]]
y = exercise_data["Weight"]

# Linear Regression
model = LinearRegression()
model.fit(X, y)
exercise_data["Predicted"] = model.predict(X)

# Plot
plt.figure(figsize=(10, 5))
plt.scatter(X, y, label="Actual")
plt.plot(X, exercise_data["Predicted"], color="red", label="Predicted")
plt.title(f"Progress Prediction for {exercise_name}")
plt.xlabel("Days since first workout")
plt.ylabel("Weight")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# Add engineered features
data["Volume"] = data["Weight"] * data["Reps"]
data["Hour"] = pd.to_datetime(data["Timestamp"]).dt.hour

# Keep important columns
df = data[["Weight", "Reps", "PreMood", "PostMood", "WorkoutAim", "Name", "Hour"]].dropna()

# One-hot encode categorical
df_encoded = pd.get_dummies(df, columns=["WorkoutAim", "Name"], drop_first=True)

# Define features and target
X = df_encoded.drop(columns=["Weight"])
y = df_encoded["Weight"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit Random Forest
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Evaluate
y_pred = rf.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Random Forest MSE: {mse:.2f}")

# Feature importances
importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nTop Factors for Progress:\n", importances.head(10))
