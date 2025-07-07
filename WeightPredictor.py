import os
import pandas as pd
import numpy as np
from pandas import to_datetime
from datetime import  datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

base_dir = os.path.dirname(__file__)
file_path = os.path.abspath(os.path.join(base_dir, "..", "TestingData", "weightlog.csv"))

# Load Data
df = pd.read_csv(file_path)
df["Timestamp"] = to_datetime(df["Timestamp"])
print(df.head())

def predict_days_to_target(target_weight):
    # Create X and y
    X = df["Timestamp"].astype('int64').values.reshape(-1, 1)
    y = df["WeightKg"]
    X_train, X_test, y_train, y_test= train_test_split(X, y, random_state=42)

    # LR model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Estimate when predicted = target
    last_date = df["Timestamp"].max()
    last_int = int(last_date.timestamp() * 1e9) # convert to nanoseconds

    for i in range(1, 1825): # Predict at least 5 years into future
        future_date = last_date + timedelta(days=i)
        future_int = int(future_date.timestamp() * 1e9)
        predicted_weight = model.predict(np.array([[future_int]]))[0]
        if predicted_weight >= target_weight:
            return i # days until target
    return None

    print("model.coef_: {}".format(model.coef_))
    print("model.intercept_: {}".format(model.intercept_))

    print("Training score: {:.2f}".format(model.score(X_train, y_train)))
    print("Test score: {:.2f}".format(model.score(X_test, y_test)))

