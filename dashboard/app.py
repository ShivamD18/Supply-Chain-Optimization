import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from scipy.stats import norm

st.set_page_config(
    page_title="ESAB Logistics & Inventory Intelligence",
    page_icon="📦",
    layout="wide"
)

@st.cache_data
def load_all_data():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_path, "data", "processed")
    raw_dir = os.path.join(base_path, "data", "raw")
    
    orders = pd.read_csv(os.path.join(data_dir, "cleaned_logistics_data.csv"))
    products = pd.read_csv(os.path.join(raw_dir, "product_master.csv"))
    inventory_eoq = pd.read_csv(os.path.join(data_dir, "comprehensive_inventory_model.csv"))
    supplier_opt = pd.read_csv(os.path.join(data_dir, "optimal_supplier_allocation.csv"))
    model_benchmarks = pd.read_csv(os.path.join(data_dir, "model_benchmark_results.csv"))
    
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["delivery_date"] = pd.to_datetime(orders["delivery_date"])
    return orders, products, inventory_eoq, supplier_opt, model_benchmarks

orders_df, products_df, inv_eoq_df, supplier_opt_df, benchmarks_df = load_all_data()

st.title("📦 Supply Chain & Inventory Control Tower")
st.markdown("Real-time operational monitoring, ML demand forecasting, EOQ policies, and LP supplier allocation.")

# Sidebar Controls
st.sidebar.header("Operational Controls")
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

# Using SciPy for exact standard normal quantile calculation
z_score = float(norm.ppf(service_level / 100.0))

filtered_orders = orders_df[orders_df["category"].isin(selected_category)]
filtered_eoq = inv_eoq_df[inv_eoq_df["category"].isin(selected_category)]

# High-Level Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Procurement Spend", f"${filtered_orders['total_cost'].sum():,.2f}")
col2.metric("On-Time Delivery Rate", f"{(filtered_orders['is_on_time'].mean() * 100):.1f}%")
col3.metric("Avg Lead Time", f"{filtered_orders['actual_lead_time_days'].mean():.1f} Days")
col4.metric("Active SKUs Monitored", len(filtered_eoq))

st.divider()

# Tab Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Logistics & Suppliers", 
    "📈 ML Demand Forecasting", 
    "⚙️ Inventory & EOQ Policy", 
    "🎯 LP Supplier Optimization", 
    "📋 Master Orders"
])

# ----------------- TAB 1: LOGISTICS & SUPPLIERS -----------------
with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        fig_supplier = px.box(
            filtered_orders,
            x="supplier",
            y="actual_lead_time_days",
            color="supplier",
            title="Lead Time Distribution by Supplier (Days)"
        )
        st.plotly_chart(fig_supplier, use_container_width=True)
    with col_b:
        fig_pie = px.pie(
            filtered_orders["po_status"].value_counts().reset_index(),
            names="po_status",
            values="count",
            title="Purchase Order Status Breakdown",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ----------------- TAB 2: ML DEMAND FORECASTING -----------------
with tab2:
    st.subheader("Machine Learning Model Validation & Comparison (Stage 7)")
    st.dataframe(benchmarks_df, use_container_width=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        fig_mae = px.bar(
            benchmarks_df,
            x="Model",
            y="MAE",
            color="Model",
            title="Mean Absolute Error (Lower is Better)"
        )
        st.plotly_chart(fig_mae, use_container_width=True)
    with col_m2:
        fig_wape = px.bar(
            benchmarks_df,
            x="Model",
            y="WAPE (%)",
            color="Model",
            title="Weighted Absolute Percentage Error (WAPE %)"
        )
        st.plotly_chart(fig_wape, use_container_width=True)

# ----------------- TAB 3: INVENTORY & EOQ POLICY -----------------
with tab3:
    st.subheader(f"Multi-Echelon Inventory Policies @ {service_level:.1f}% Service Level (Z = {z_score:.2f})")
    
    # Interactive recalculation of Safety Stock & ROP based on SciPy Z-score
    sim_eoq = filtered_eoq.copy()
    sim_eoq["dyn_safety_stock"] = np.ceil(z_score * sim_eoq["std_lead_days"] * sim_eoq["daily_demand"]).astype(int)
    sim_eoq["dyn_rop"] = np.ceil((sim_eoq["daily_demand"] * sim_eoq["mean_lead_days"]) + sim_eoq["dyn_safety_stock"]).astype(int)
    sim_eoq["capital_savings_$"] = (sim_eoq["safety_stock"] - sim_eoq["dyn_safety_stock"]) * sim_eoq["unit_cost"]

    fig_inv = go.Figure(data=[
        go.Bar(name='Static Safety Stock (Baseline)', x=sim_eoq['sku'], y=sim_eoq['safety_stock'], marker_color='#94a3b8'),
        go.Bar(name='Optimized Dynamic Safety Stock', x=sim_eoq['sku'], y=sim_eoq['dyn_safety_stock'], marker_color='#0284c7'),
        go.Bar(name='Economic Order Quantity (EOQ)', x=sim_eoq['sku'], y=sim_eoq['eoq_units'], marker_color='#10b981'),
        go.Bar(name='Reorder Point (ROP)', x=sim_eoq['sku'], y=sim_eoq['dyn_rop'], marker_color='#f59e0b')
    ])
    fig_inv.update_layout(barmode='group', title="Inventory Policy Comparison: EOQ, Safety Stock, and ROP", xaxis_title="SKU", yaxis_title="Units")
    st.plotly_chart(fig_inv, use_container_width=True)
    
    st.dataframe(sim_eoq[[
        "sku", "category", "unit_cost", "annual_demand", "eoq_units", 
        "dyn_safety_stock", "dyn_rop", "capital_savings_$"
    ]].rename(columns={
        "unit_cost": "Unit Cost ($)",
        "annual_demand": "Annual Demand",
        "eoq_units": "EOQ (Units)",
        "dyn_safety_stock": "Dynamic Safety Stock",
        "dyn_rop": "Reorder Point (ROP)",
        "capital_savings_$": "Working Capital Impact ($)"
    }), use_container_width=True)

# ----------------- TAB 4: LP SUPPLIER OPTIMIZATION -----------------
with tab4:
    st.subheader("Linear Programming Order Allocation Optimization (Stage 9)")
    st.markdown(r"Optimal cost-minimizing order allocation subject to vendor capacities and a maximum allowable delay tolerance ($\le 6\%$).")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.dataframe(supplier_opt_df, use_container_width=True)
        st.info(f"Total Minimized Procurement Spend: **${supplier_opt_df['Total_Cost'].sum():,.2f}**")
    with col_s2:
        fig_alloc = px.pie(
            supplier_opt_df,
            names="Supplier",
            values="Allocated_Units",
            title="Optimized Order Quantity Allocation (Units)",
            hole=0.4
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

# ----------------- TAB 5: MASTER ORDERS -----------------
with tab5:
    st.subheader("Purchase Order Stream & Master Records")
    st.dataframe(
        filtered_orders[[
            "po_number", "sku", "category", "supplier", "order_date", 
            "delivery_date", "expected_lead_time_days", "actual_lead_time_days", 
            "lead_time_variance", "po_status", "total_cost"
        ]].sort_values(by="order_date", ascending=False),
        use_container_width=True
    )