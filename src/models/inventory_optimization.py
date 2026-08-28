import pandas as pd
import numpy as np

def calculate_inventory_policies(z_service_level=1.65): # 1.65 corresponds to a 95% cycle service level
    df = pd.read_csv("data/processed/cleaned_logistics_data.csv")
    products = pd.read_csv("data/raw/product_master.csv")
    
    # Calculate Lead Time Statistics per SKU
    lead_time_stats = df.groupby("sku").agg(
        avg_actual_lead_time=("actual_lead_time_days", "mean"),
        std_actual_lead_time=("actual_lead_time_days", "std"),
        total_ordered=("order_quantity", "sum")
    ).reset_index()
    
    # Estimate Average Daily Demand (assuming 365-day operational year)
    lead_time_stats["avg_daily_demand"] = lead_time_stats["total_ordered"] / 365.0
    
    # Merge with Master Data
    merged = pd.merge(products, lead_time_stats, on="sku")
    
    # Dynamic Safety Stock: SS = Z * (std_lead_time * avg_daily_demand)
    merged["dynamic_safety_stock"] = (
        z_service_level * merged["std_actual_lead_time"] * merged["avg_daily_demand"]
    ).apply(np.ceil).astype(int)
    
    # Reorder Point: ROP = (avg_daily_demand * avg_actual_lead_time) + dynamic_safety_stock
    merged["reorder_point"] = (
        (merged["avg_daily_demand"] * merged["avg_actual_lead_time"]) + merged["dynamic_safety_stock"]
    ).apply(np.ceil).astype(int)
    
    # Compare against Static Baseline
    merged["stock_reduction_units"] = merged["safety_stock"] - merged["dynamic_safety_stock"]
    merged["working_capital_savings_$"] = merged["stock_reduction_units"] * merged["unit_cost"]
    
    output_cols = [
        "sku", "category", "unit_cost", "avg_daily_demand", 
        "avg_actual_lead_time", "dynamic_safety_stock", "safety_stock", 
        "reorder_point", "working_capital_savings_$"
    ]
    
    results = merged[output_cols].sort_values(by="working_capital_savings_$", ascending=False)
    
    print("=== DYNAMIC INVENTORY POLICY SUMMARY ===")
    print(results.to_string(index=False))
    
    total_savings = results["working_capital_savings_$"].sum()
    print(f"\nEstimated Working Capital Optimization Potential: ${total_savings:,.2f}")
    
    results.to_csv("data/processed/inventory_policy_recommendations.csv", index=False)
    print("Recommendations saved to data/processed/inventory_policy_recommendations.csv")

if __name__ == "__main__":
    calculate_inventory_policies()