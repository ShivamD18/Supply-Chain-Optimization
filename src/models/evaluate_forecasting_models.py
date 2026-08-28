import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

df = pd.read_csv("data/processed/demand_features.csv")
df["order_date"] = pd.to_datetime(df["order_date"])

# Time-based Train-Test Split (80% train, 20% test)
split_date = df["order_date"].quantile(0.8)
train = df[df["order_date"] <= split_date]
test = df[df["order_date"] > split_date]

features = [c for c in df.columns if "lag_" in c or "rolling_" in c or c in ["day_of_week", "month"]]
target = "order_quantity"

# Model 1: Baseline 7-day Moving Average
test_baseline = test["rolling_mean_7"]

# Model 2: Random Forest ML Model
rf = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42)
rf.fit(train[features], train[target])
test_rf = rf.predict(test[features])

def calculate_metrics(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    wape = (np.sum(np.abs(y_true - y_pred)) / np.sum(y_true)) * 100
    return {"Model": model_name, "MAE": mae, "RMSE": rmse, "WAPE (%)": wape}

results = pd.DataFrame([
    calculate_metrics(test[target], test_baseline, "Baseline (7-Day Rolling Mean)"),
    calculate_metrics(test[target], test_rf, "Random Forest Demand Forecaster")
])

print("=== FORECASTING MODEL BENCHMARK RESULTS ===")
print(results.to_string(index=False))
results.to_csv("data/processed/model_benchmark_results.csv", index=False)