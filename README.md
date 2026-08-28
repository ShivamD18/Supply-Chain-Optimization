# Supply Chain Optimization & Logistics Intelligence Platform

An end-to-end analytics engine and interactive operational control tower designed to forecast lead-time variability, automate inventory replenishment policies (Dynamic Safety Stock & ROP), and generate executive master data reports.

---

## 🏗️ Architecture & Core Modules

1. **Data Ingestion & Pipeline (`src/data/`)**: Automated extraction, transformation, and schema validation for SKU master data and purchase order logistics streams.
2. **Predictive Modeling (`src/models/`)**: 
   - **Lead-Time Regression**: Random Forest models forecasting transit variance and supplier delivery durations.
   - **Shipment Delay Classification**: Risk modeling identifying probability of operational bottlenecks.
   - **Dynamic Inventory Engine**: Computes stochastic Reorder Points ($ROP$) and Safety Stock ($SS = Z \times \sigma_L \times D$) to optimize working capital.
3. **Interactive Control Tower (`dashboard/app.py`)**: Real-time Streamlit dashboard with dynamic service level tuning, supplier scorecarding, and delay tracking.
4. **Automated Executive Reporting (`src/reports/`)**: Automated generation of stylized, multi-tab Excel workbooks (`openpyxl`) for supplier evaluation and exception management.

---

## 🚀 Quickstart

```powershell
# 1. Activate Environment
.venv\Scripts\Activate.ps1

# 2. Run Data Pipeline & Optimization Engine
python src/data/generate_supply_chain_data.py
python src/data/load_and_validate.py
python src/models/train_lead_time_model.py
python src/models/inventory_optimization.py

# 3. Generate Executive Excel Report
python src/reports/generate_executive_report.py

# 4. Launch Interactive Dashboard
python -m streamlit run dashboard/app.py