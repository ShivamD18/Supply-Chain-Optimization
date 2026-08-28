import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
n_orders = 1200

# 1. Product Master Data
products = [
    {"sku": "WLD-001", "category": "Welding Consumables", "unit_cost": 45.0, "unit_price": 75.0, "safety_stock": 150, "lead_time_days": 14},
    {"sku": "GAS-002", "category": "Gas Control Regulators", "unit_cost": 120.0, "unit_price": 210.0, "safety_stock": 60, "lead_time_days": 21},
    {"sku": "FAB-003", "category": "Connected Fabrication Units", "unit_cost": 1450.0, "unit_price": 2300.0, "safety_stock": 20, "lead_time_days": 35},
    {"sku": "ACC-004", "category": "Safety & PPE", "unit_cost": 15.0, "unit_price": 32.0, "safety_stock": 300, "lead_time_days": 7},
    {"sku": "CUT-005", "category": "Plasma Cutting Spares", "unit_cost": 85.0, "unit_price": 140.0, "safety_stock": 80, "lead_time_days": 18}
]
df_products = pd.DataFrame(products)

# 2. Purchase Orders & Logistics Transactions
start_date = datetime(2025, 1, 1)
suppliers = ["Supplier Alpha", "Supplier Beta", "Supplier Gamma", "Logistics Global"]
statuses = ["Delivered", "In Transit", "Delayed", "Cancelled"]

po_records = []
for i in range(1, n_orders + 1):
    prod = np.random.choice(products)
    order_date = start_date + timedelta(days=int(np.random.randint(0, 365)))
    expected_lead = prod["lead_time_days"]
    actual_lead = int(np.random.normal(loc=expected_lead + 1, scale=3))
    actual_lead = max(2, actual_lead)
    
    delivery_date = order_date + timedelta(days=actual_lead)
    quantity = int(np.random.choice([25, 50, 100, 200, 500]))
    status = "Delayed" if actual_lead > expected_lead + 3 else np.random.choice(statuses, p=[0.80, 0.12, 0.05, 0.03])
    
    po_records.append({
        "po_number": f"PO-{10000 + i}",
        "sku": prod["sku"],
        "category": prod["category"],
        "supplier": np.random.choice(suppliers),
        "order_date": order_date.strftime("%Y-%m-%d"),
        "expected_lead_time_days": expected_lead,
        "actual_lead_time_days": actual_lead,
        "delivery_date": delivery_date.strftime("%Y-%m-%d"),
        "order_quantity": quantity,
        "unit_cost": prod["unit_cost"],
        "total_cost": quantity * prod["unit_cost"],
        "po_status": status,
        "warehouse_location": "Mississauga Facility"
    })

df_orders = pd.DataFrame(po_records)

# Save datasets to raw directory
df_products.to_csv("data/raw/product_master.csv", index=False)
df_orders.to_csv("data/raw/purchase_orders_logistics.csv", index=False)
print("Stage 2 Data Generation Complete: Saved to data/raw/")