import numpy as np
import matplotlib.pyplot as plt

time_balance_point = 65.02
I_values = np.logspace(np.log2(0.5), np.log2(8192), 200, base=2)
constant_flop_energy_efficiency = 0.786
energy_balance_point = 515.46

temp = constant_flop_energy_efficiency * energy_balance_point
P_values = 1 / (1 + (temp + ((1 - constant_flop_energy_efficiency) * np.maximum(0, time_balance_point - I_values))) / I_values)

# Plot Roofline Model
plt.figure(figsize=(8, 6))
plt.loglog(I_values, P_values, label='Roofline (GFLOP/s)', color='blue')

# Add vertical line at I_threshold
plt.axvline(energy_balance_point, linestyle='--', color='black', alpha=0.6)
plt.text(energy_balance_point * 1.2, 1/140, f'{energy_balance_point:.1f}', color='blue')

# Customize x and y ticks for better readability
xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
yticks = [1/32, 1/16, 1/8, 1/4, 1/2, 1]
plt.xticks(xticks, [f"{x:.0f}" for x in xticks], fontsize=6)
plt.yticks(yticks, [f"{y}" for y in yticks], fontsize=6)

plt.xlabel('Operational Intensity (FLOPs/Byte)')
plt.ylabel('Performance (8,043GFLOPs/Joule)')
plt.title('Roofline Model for Intel Core i9-13900K')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# Save plot
plt.savefig("roofline_energy.png")
plt.close()