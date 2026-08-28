import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="ESAB Logistics & Inventory Intelligence",
    page_icon="📦",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    orders_path = os.path.join(base_path, "data", "processed", "cleaned_logistics_data.csv")
    products_path = os.path.join(base_path, "data", "raw", "product_master.csv")
    
    orders = pd.read_csv(orders_path)
    products = pd.read_csv(products_path)
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["delivery_date"] = pd.to_datetime(orders["delivery_date"])
    return orders, products

orders_df, products_df = load_data()

# Header
st.title("📦 Supply Chain & Inventory Control Tower")
st.markdown("Operational analytics, lead-time variance tracking, and dynamic safety stock optimization.")

# Sidebar Controls
st.sidebar.header("Operational Parameters")
selected_category = st.sidebar.multiselect(
    "Filter Categories",
    options=products_df["category"].unique(),
    default=products_df["category"].unique()
)

service_level = st.sidebar.slider(
    "Target Cycle Service Level (%)",
    min_value=80.0,
    max_value=99.9,
    value=95.0,
    step=0.5
)

# Map service level percentage to Z-score
z_lookup = {
    80.0: 0.84, 85.0: 1.04, 90.0: 1.28, 95.0: 1.65, 
    97.5: 1.96, 99.0: 2.33, 99.9: 3.09
}
# Approximate Z-score calculation for arbitrary values in slider
from scipy.stats import norm
z_score = norm.ppf(service_level / 100.0)

filtered_orders = orders_df[orders_df["category"].isin(selected_category)]
filtered_products = products_df[products_df["category"].isin(selected_category)]

# Top KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)
total_spend = filtered_orders["total_cost"].sum()
on_time_pct = filtered_orders["is_on_time"].mean() * 100
avg_lead_time = filtered_orders["actual_lead_time_days"].mean()
delayed_shipments = (~filtered_orders["is_on_time"]).sum()

col1.metric("Total Procurement Spend", f"${total_spend:,.2f}")
col2.metric("On-Time Delivery Rate", f"{on_time_pct:.1f}%", delta=f"{on_time_pct - 90:.1f}% vs Target")
col3.metric("Avg Actual Lead Time", f"{avg_lead_time:.1f} Days")
col4.metric("Delayed Purchase Orders", f"{delayed_shipments} Orders", delta_color="inverse")

st.divider()

# Tab Navigation
tab1, tab2, tab3 = st.tabs(["📊 Supplier & Logistics Analytics", "⚙️ Dynamic Inventory Optimization", "📋 Purchase Order Tracker"])

with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Lead Time Variance by Supplier
        fig_supplier = px.box(
            filtered_orders,
            x="supplier",
            y="actual_lead_time_days",
            color="supplier",
            title="Lead Time Distribution by Supplier (Days)",
            labels={"actual_lead_time_days": "Actual Lead Time (Days)", "supplier": "Supplier"}
        )
        st.plotly_chart(fig_supplier, use_container_width=True)
        
    with col_b:
        # Order Status Distribution
        status_counts = filtered_orders["po_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_pie = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Purchase Order Status Breakdown",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader(f"Dynamic Policy Simulation @ {service_level:.1f}% Service Level (Z = {z_score:.2f})")
    
    # Recalculate dynamic safety stock and ROP based on interactive Z-score
    lead_stats = filtered_orders.groupby("sku").agg(
        avg_lead=("actual_lead_time_days", "mean"),
        std_lead=("actual_lead_time_days", "std"),
        total_qty=("order_quantity", "sum")
    ).reset_index()
    
    lead_stats["std_lead"] = lead_stats["std_lead"].fillna(0)
    lead_stats["avg_daily_demand"] = lead_stats["total_qty"] / 365.0
    
    inv_sim = pd.merge(filtered_products, lead_stats, on="sku")
    inv_sim["dyn_safety_stock"] = np.ceil(z_score * inv_sim["std_lead"] * inv_sim["avg_daily_demand"]).astype(int)
    inv_sim["reorder_point"] = np.ceil((inv_sim["avg_daily_demand"] * inv_sim["avg_lead"]) + inv_sim["dyn_safety_stock"]).astype(int)
    inv_sim["stock_diff"] = inv_sim["safety_stock"] - inv_sim["dyn_safety_stock"]
    inv_sim["capital_impact_$"] = inv_sim["stock_diff"] * inv_sim["unit_cost"]
    
    # Comparison Chart
    fig_stock = go.Figure(data=[
        go.Bar(name='Static Safety Stock (Baseline)', x=inv_sim['sku'], y=inv_sim['safety_stock'], marker_color='#94a3b8'),
        go.Bar(name='Optimized Safety Stock (Dynamic)', x=inv_sim['sku'], y=inv_sim['dyn_safety_stock'], marker_color='#0284c7'),
        go.Bar(name='Recommended Reorder Point (ROP)', x=inv_sim['sku'], y=inv_sim['reorder_point'], marker_color='#f59e0b')
    ])
    fig_stock.update_layout(
        barmode='group',
        title="Baseline vs. Dynamic Safety Stock & Reorder Point Comparison",
        xaxis_title="SKU",
        yaxis_title="Units"
    )
    st.plotly_chart(fig_stock, use_container_width=True)
    
    # Capital summary table
    total_savings = inv_sim["capital_impact_$"].sum()
    if total_savings >= 0:
        st.success(f"💡 Potential Working Capital Release: **${total_savings:,.2f}** without compromising service levels.")
    else:
        st.warning(f"⚠️ Required Additional Safety Investment: **${abs(total_savings):,.2f}** to sustain {service_level}% service level.")
        
    st.dataframe(
        inv_sim[[
            "sku", "category", "unit_cost", "avg_daily_demand", 
            "avg_lead", "safety_stock", "dyn_safety_stock", "reorder_point", "capital_impact_$"
        ]].rename(columns={
            "avg_daily_demand": "Daily Demand",
            "avg_lead": "Avg Lead Time (Days)",
            "safety_stock": "Baseline SS",
            "dyn_safety_stock": "Dynamic SS",
            "reorder_point": "ROP (Units)",
            "capital_impact_$": "Working Capital Impact ($)"
        }),
        use_container_width=True
    )

with tab3:
    st.subheader("Recent Purchase Orders & Operational Exceptions")
    st.dataframe(
        filtered_orders[[
            "po_number", "sku", "category", "supplier", "order_date", 
            "delivery_date", "expected_lead_time_days", "actual_lead_time_days", 
            "lead_time_variance", "po_status", "total_cost"
        ]].sort_values(by="order_date", ascending=False),
        use_container_width=True
    )