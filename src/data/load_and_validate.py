import pandas as pd

def load_and_inspect():
    orders_df = pd.read_csv("data/raw/purchase_orders_logistics.csv")
    products_df = pd.read_csv("data/raw/product_master.csv")
    
    # Type conversion
    orders_df["order_date"] = pd.to_datetime(orders_df["order_date"])
    orders_df["delivery_date"] = pd.to_datetime(orders_df["delivery_date"])
    
    # Calculate Lead Time Variance (KPI for ESAB logistics)
    orders_df["lead_time_variance"] = orders_df["actual_lead_time_days"] - orders_df["expected_lead_time_days"]
    orders_df["is_on_time"] = orders_df["lead_time_variance"] <= 0

    print("=== DATA SUMMARY ===")
    print(f"Total Purchase Orders: {len(orders_df)}")
    print(f"On-Time Delivery Rate: {(orders_df['is_on_time'].mean() * 100):.2f}%")
    print(f"Average Lead Time Variance: {orders_df['lead_time_variance'].mean():.2f} days")
    
    # Save cleaned master file for analytics and modeling
    orders_df.to_csv("data/processed/cleaned_logistics_data.csv", index=False)
    print("\nProcessed dataset successfully created at data/processed/cleaned_logistics_data.csv")

if __name__ == "__main__":
    load_and_inspect()