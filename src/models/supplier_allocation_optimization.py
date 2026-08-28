import numpy as np
import pandas as pd
from scipy.optimize import linprog

# Suppliers for Welding Consumables (WLD-001)
suppliers = ["Supplier Alpha", "Supplier Beta", "Supplier Gamma"]
unit_prices = [45.0, 43.5, 47.0]          # Cost per unit
on_time_rates = [0.96, 0.88, 0.98]        # Reliability metric
max_capacities = [800, 600, 1000]         # Supplier monthly capacity limits
total_demand_required = 1400              # Units required

# Linear Programming formulation:
# Min sum(unit_prices[i] * x[i])
# Subject to:
# 1. sum(x[i]) >= total_demand_required
# 2. sum((1 - on_time_rates[i]) * x[i]) <= 0.06 * total_demand_required (Max 6% delay rate)
# 3. 0 <= x[i] <= max_capacities[i]

c = unit_prices

# Inequality constraints (A_ub * x <= b_ub)
A_ub = [
    [-1, -1, -1],                                             # Demand constraint (-x1 - x2 - x3 <= -1400)
    [1 - on_time_rates[0], 1 - on_time_rates[1], 1 - on_time_rates[2]] # Defect/delay tolerance
]
b_ub = [-total_demand_required, 0.06 * total_demand_required]

bounds = [(0, cap) for cap in max_capacities]

res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

if res.success:
    allocation = pd.DataFrame({
        "Supplier": suppliers,
        "Allocated_Units": np.round(res.x, 0),
        "Unit_Price": unit_prices,
        "Total_Cost": np.round(res.x * unit_prices, 2)
    })
    print("=== OPTIMAL SUPPLIER ORDER ALLOCATION ===")
    print(allocation.to_string(index=False))
    print(f"\nTotal Minimized Procurement Spend: ${res.fun:,.2f}")
    allocation.to_csv("data/processed/optimal_supplier_allocation.csv", index=False)