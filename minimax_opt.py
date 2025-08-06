############# Author: FreeCurryAU on 7th of August 2025  ###########################################################

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Define DPI values and their corresponding empirical SNR measurements
dpi_values = np.array([400, 800, 1600, 3200, 6400])
snr_values = np.array([0.95, 0.90, 0.83, 0.70, 0.55])  # Replace with your measurements if needed

# Constants
D_max = dpi_values.max()
SNR_max = snr_values.max()
alpha = 0.0005
e0 = 300
w_A_max = 0.4

# Defined fixed eDPI (use CS2 units!)
fixed_eDPI = 1100

# Functions
def cost_A(D: float) -> float:
    return 1 - (D / D_max)

def cost_B(SNR_D: float) -> float:
    return 1 - (SNR_D / SNR_max)

def w_A(e: float) -> float:
    return w_A_max * (1 - np.exp(-alpha * (e - e0)))

def w_B(e: float) -> float:
    return 1 - w_A(e)

# Compute fixed weights from user eDPI
wa = w_A(fixed_eDPI)
wb = w_B(fixed_eDPI)

# Evaluate costs at all DPI values
results = []
for D, SNR_D in zip(dpi_values, snr_values):
    ca = cost_A(D)
    cb = cost_B(SNR_D)
    total_cost = max(wa * ca, wb * cb)
    in_game_sens = fixed_eDPI / D
    results.append({
        "DPI": D,
        "SNR": SNR_D,
        "InGameSens": in_game_sens,
        "Cost_A": ca,
        "Cost_B": cb,
        "w_A": wa,
        "w_B": wb,
        "TotalCost": total_cost
    })

# Convert to DataFrame
df = pd.DataFrame(results)
optimal_row = df.loc[df["TotalCost"].idxmin()]
optimal_dpi = optimal_row["DPI"]
optimal_sens = optimal_row["InGameSens"]

print(optimal_dpi)
