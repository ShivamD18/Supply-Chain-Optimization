import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

os.makedirs("models", exist_ok=True)

# 1. Load data and aggregate to daily/weekly demand per SKU
orders_df = pd.read_csv("data/processed/cleaned_logistics_data.csv")
orders_df["order_date"] = pd.to_datetime(orders_df["order_date"])

# Create daily time series per SKU
daily_demand = orders_df.groupby(["order_date", "sku"])["order_quantity"].sum().reset_index()

# Complete date grid so zero-demand days are represented
sku_list = daily_demand["sku"].unique()
date_range = pd.date_range(start=daily_demand["order_date"].min(), end=daily_demand["order_date"].max(), freq="D")
full_grid = pd.MultiIndex.from_product([date_range, sku_list], names=["order_date", "sku"]).to_frame().reset_index(drop=True)

df_ts = pd.merge(full_grid, daily_demand, on=["order_date", "sku"], how="left").fillna({"order_quantity": 0})
df_ts = df_ts.sort_values(by=["sku", "order_date"]).reset_index(drop=True)

# 2. Feature Engineering: Lags & Rolling Statistics
for lag in [1, 7, 14, 30]:
    df_ts[f"lag_{lag}"] = df_ts.groupby("sku")["order_quantity"].shift(lag)

for window in [7, 14, 30]:
    df_ts[f"rolling_mean_{window}"] = df_ts.groupby("sku")["order_quantity"].shift(1).rolling(window).mean()
    df_ts[f"rolling_std_{window}"] = df_ts.groupby("sku")["order_quantity"].shift(1).rolling(window).std()

df_ts["day_of_week"] = df_ts["order_date"].dt.dayofweek
df_ts["month"] = df_ts["order_date"].dt.month
df_ts = df_ts.dropna().reset_index(drop=True)

# Save processed forecasting feature dataset
df_ts.to_csv("data/processed/demand_features.csv", index=False)
print("Demand feature engineering complete. Ready for model validation.")