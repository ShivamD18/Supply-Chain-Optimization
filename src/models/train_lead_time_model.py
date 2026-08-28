import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, classification_report
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Ensure output directory exists
os.makedirs("models", exist_ok=True)

# 1. Load data
df = pd.read_csv("data/processed/cleaned_logistics_data.csv")
df["order_date"] = pd.to_datetime(df["order_date"])
df["order_month"] = df["order_date"].dt.month
df["order_dayofweek"] = df["order_date"].dt.dayofweek

# 2. Define Features & Targets
categorical_features = ["sku", "category", "supplier"]
numeric_features = ["expected_lead_time_days", "order_quantity", "order_month", "order_dayofweek"]

X = df[categorical_features + numeric_features]
y_reg = df["actual_lead_time_days"]
y_clf = (~df["is_on_time"]).astype(int)  # 1 = Delayed, 0 = On-Time

# 3. Train-Test Split
X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
    X, y_reg, y_clf, test_size=0.2, random_state=42
)

# 4. Preprocessing Pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(drop="first", sparse_output=False), categorical_features),
        ("num", "passthrough", numeric_features),
    ]
)

# 5. Regression Model: Predict Exact Lead Time
reg_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])
reg_pipeline.fit(X_train, y_reg_train)
y_reg_pred = reg_pipeline.predict(X_test)

# 6. Classification Model: Predict Likelihood of Shipment Delay
clf_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])
clf_pipeline.fit(X_train, y_clf_train)
y_clf_pred = clf_pipeline.predict(X_test)

print("=== LEAD TIME REGRESSION PERFORMANCE ===")
print(f"R² Score: {r2_score(y_reg_test, y_reg_pred):.3f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_reg_test, y_reg_pred)):.2f} days\n")

print("=== SHIPMENT DELAY CLASSIFICATION REPORT ===")
print(classification_report(y_clf_test, y_clf_pred, target_names=["On-Time", "Delayed"]))