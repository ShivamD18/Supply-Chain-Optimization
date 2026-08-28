# Supply Chain Analytics & Inventory Optimization Engine

An end-to-end data pipeline, predictive modeling engine, and interactive control tower designed to optimize enterprise logistics. This platform mitigates supplier lead-time variability, automates inventory replenishment (EOQ/ROP), and minimizes procurement costs through constrained optimization, providing actionable intelligence via Streamlit and Power BI.

---

## 🏗️ Architecture & Core Modules

The system is built on a modular Python architecture, integrating machine learning, operations research, and automated reporting:

1. **Data Engineering (`src/data/`)**: Automated ingestion, schema validation, and synthetic multi-tier transaction generation spanning SKU master records and purchase order histories.
2. **Machine Learning & Forecasting (`src/models/`)**: 
   - **Demand Forecasting:** Random Forest regression pipelines benchmarking lag features and rolling statistics against baseline moving averages (evaluated via MAE, RMSE, and WAPE).
   - **Lead-Time Classification:** Predictive risk modeling to identify the probability of shipment delays based on historical supplier variance.
3. **Operations Research & Optimization (`src/models/`)**:
   - **Inventory Replenishment Engine:** Computes Economic Order Quantity (EOQ) and stochastic Safety Stock to balance holding costs against target cycle service levels.
   - **Supplier Allocation Solver:** Linear Programming (LP) via `scipy.optimize` to minimize total procurement spend while adhering to strict supplier capacity limits and maximum defect/delay tolerances.
4. **Interactive Control Tower (`dashboard/app.py`)**: Real-time Streamlit dashboard enabling dynamic parameter tuning (e.g., target Z-scores for service levels), supplier scorecarding, and working capital simulations.
5. **Enterprise BI & Reporting (`src/reports/`)**: 
   - Automated generation of stylized, multi-tab Excel master workbooks using `openpyxl`.
   - Power BI integration featuring DAX-calculated KPIs for operational tracking.

---

## 🧮 Mathematical Formulations

The optimization engine relies on standard operations research models to dynamically calculate inventory parameters:

**1. Economic Order Quantity (EOQ)**
Calculates the optimal order size to minimize the combined costs of ordering and holding inventory:
**EOQ = √ ( (2 × D × S) / H )**
*Where D = Annual Demand, S = Fixed Ordering Cost, and H = Annual Holding Cost per unit.*

**2. Dynamic Safety Stock (SS)**
Buffers against lead-time volatility to maintain a designated cycle service level:
**SS = Z × σ_L × D_avg**
*Where Z = Service Level Z-Score, σ_L = Lead Time Standard Deviation, and D_avg = Average Daily Demand.*

**3. Reorder Point (ROP)**
The inventory threshold triggering a new purchase order:
**ROP = (D_avg × L_avg) + SS**
*Where L_avg = Average Lead Time in days.*

**4. Supplier Allocation Optimization (Linear Programming)**
Minimizes procurement costs across competing suppliers subject to constraints:
**Minimize: Σ (C_i × X_i)**
*Subject to: Total Units ≥ Demand, Vendor Units ≤ Capacity, and Delayed Units ≤ Max Tolerance.*

---

## 📂 Project Structure

```text
supply-chain-optimization/
├── data/
│   ├── raw/                           # Immutable SKU and initial state data
│   └── processed/                     # Engineered features, EOQ models, and LP outputs
├── src/
│   ├── data/
│   │   ├── generate_supply_chain_data.py
│   │   └── load_and_validate.py
│   ├── models/
│   │   ├── demand_forecasting.py
│   │   ├── evaluate_forecasting_models.py
│   │   ├── inventory_policy_engine.py
│   │   └── supplier_allocation_optimization.py
│   └── reports/
│       ├── build_advanced_excel_model.py
│       └── generate_executive_report.py
├── dashboard/
│   ├── app.py                         # Streamlit Interactive Control Tower
│   ├── ESAB_Logistics_Control_Tower.pbix # Power BI Dashboard
│   └── ESAB_Logistics_Control_Tower.pbit
├── reports/                           # Output directory for automated Excel workbooks
├── requirements.txt                   # Project dependencies
└── README.md
