import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Merge all analytical outputs into one clean workbook
with pd.ExcelWriter("reports/Supply_Chain_Analytics_Master.xlsx", engine="openpyxl") as writer:
    pd.read_csv("data/processed/cleaned_logistics_data.csv").to_excel(writer, sheet_name="Raw_Transactions", index=False)
    pd.read_csv("data/processed/comprehensive_inventory_model.csv").to_excel(writer, sheet_name="Inventory_Policy_EOQ", index=False)
    pd.read_csv("data/processed/optimal_supplier_allocation.csv").to_excel(writer, sheet_name="Supplier_Optimization", index=False)
    pd.read_csv("data/processed/model_benchmark_results.csv").to_excel(writer, sheet_name="Model_Validation", index=False)

print("Master Analytical Excel Workbook created at reports/Supply_Chain_Analytics_Master.xlsx")