import pandas as pd
import numpy as np

# Load product data and transactions
products = pd.read_csv("data/raw/product_master.csv")
orders = pd.read_csv("data/processed/cleaned_logistics_data.csv")

# Annual Demand (D), Holding Cost (H = 20% of unit cost), Order Cost (S = $50 fixed)
annual_demand = orders.groupby("sku")["order_quantity"].sum().reset_index(name="annual_demand")
lead_time_data = orders.groupby("sku").agg(
    mean_lead_days=("actual_lead_time_days", "mean"),
    std_lead_days=("actual_lead_time_days", "std")
).reset_index()

inv_model = pd.merge(products, annual_demand, on="sku")
inv_model = pd.merge(inv_model, lead_time_data, on="sku")

ORDER_COST = 50.0   # Fixed PO processing cost
HOLDING_RATE = 0.20 # 20% holding cost rate

# 1. Economic Order Quantity (EOQ = sqrt((2 * D * S) / H))
inv_model["holding_cost_annual"] = inv_model["unit_cost"] * HOLDING_RATE
inv_model["eoq_units"] = np.ceil(
    np.sqrt((2 * inv_model["annual_demand"] * ORDER_COST) / inv_model["holding_cost_annual"])
).astype(int)

# 2. Stochastic Safety Stock (SS = Z * std_lead * daily_demand) @ 95% service level
Z = 1.65
inv_model["daily_demand"] = inv_model["annual_demand"] / 365.0
inv_model["optimized_safety_stock"] = np.ceil(
    Z * inv_model["std_lead_days"].fillna(1) * inv_model["daily_demand"]
).astype(int)

# 3. Dynamic Reorder Point (ROP = d * L + SS)
inv_model["reorder_point_rop"] = np.ceil(
    (inv_model["daily_demand"] * inv_model["mean_lead_days"]) + inv_model["optimized_safety_stock"]
).astype(int)

inv_model.to_csv("data/processed/comprehensive_inventory_model.csv", index=False)
print("Comprehensive Inventory & EOQ Model generated at data/processed/comprehensive_inventory_model.csv")