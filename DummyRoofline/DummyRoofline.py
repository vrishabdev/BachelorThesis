import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

I_values = np.logspace(np.log2(0.5), np.log2(8192), 200, base=2)

# TIME values
max_flops_time = 9.792e11 #Flop/s
memory_bandwidth = 3.195e10 #Byte/s
tau_flop = 1 / max_flops_time #s/Flop
tau_mem = 1 / memory_bandwidth #s/Byte
time_balance_point = tau_mem / tau_flop #Flop/Byte

# Roofline
P_values = np.minimum(max_flops_time, I_values * memory_bandwidth) / 1e12  # GFLOP/s

plt.figure(figsize=(8, 5))
# Shade the memory-bound region (before x_t)
plt.axvspan(min(I_values), time_balance_point, color='#808080', alpha=0.3, label='Memory-bound region')
# Shade the compute-bound region (after x_t)
plt.axvspan(time_balance_point, max(I_values), color='#36454F', alpha=0.4, label='Compute-bound region')

plt.loglog(I_values, P_values, color='red')
plt.axvline(time_balance_point, linestyle='--', color='red', alpha=0.6)

plt.xticks([30], [r"$B_{\tau}$"], fontsize=15)
plt.yticks([])

plt.xlabel('Operational Intensity (FLOP/Byte)', fontsize=12)
plt.ylabel('FLOP/s', fontsize=12)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
plt.savefig("./DummyRoofline/dummyRoofline.pdf")


# ENERGY values
pi0 = 3.71 # idle power in Joule 
max_power = 253 # Watt

max_flops_energy = 2.72597e11 / (15.35 - pi0 * 0.68614)    # Flop/Joule      of the mp_linpack benchmark
epsilon_mem = (36.47 - pi0 * 0.29946) / 8e8                # Joule/Byte      of the STREAM benchmark
epsilon_flop = (15.35 - pi0 * 0.68614) / 2.72597e10        # Joule/Flop      of the mp_linpack benchmark
energy_balance_point = epsilon_mem / epsilon_flop          # Flop/Joule

constant_energy_per_flop = pi0 * tau_flop
actual_energy_per_flop = epsilon_flop + constant_energy_per_flop
constant_flop_energy_efficiency = epsilon_flop / actual_energy_per_flop
effective_energy_balance = constant_flop_energy_efficiency * energy_balance_point
effective_energy_balance += (1 - constant_flop_energy_efficiency) * (np.maximum(0, time_balance_point - I_values))

# Archline
P_values = (1 / (1 + effective_energy_balance / I_values)) * max_flops_energy / 1e6

plt.figure(figsize=(8, 5))
# Shade the region (before x_e)
plt.axvspan(min(I_values), energy_balance_point, color='#808080', alpha=0.3, label='not energy efficient')
# Shade the region (after x_e)
plt.axvspan(energy_balance_point, max(I_values), color='#36454F', alpha=0.4, label='energy efficient')

plt.loglog(I_values, P_values, color='blue')
plt.axvline(energy_balance_point, linestyle='--', color='blue', alpha=0.6)

plt.xticks([94], [r"$B_{\epsilon}$"], fontsize=15)
plt.yticks([])

plt.xlabel('Operational Intensity (FLOP/Byte)', fontsize=12)
plt.ylabel('FLOP/J', fontsize=12)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
plt.savefig("./DummyRoofline/dummyArchline.pdf")

# POWER values
pi_flop = epsilon_flop / tau_flop

# Powerline
temp = pi_flop / constant_flop_energy_efficiency
temp2 = np.minimum(I_values, time_balance_point) / time_balance_point
temp2 += (effective_energy_balance / np.maximum(I_values, time_balance_point))
P_values = (temp * temp2) / 10e2

plt.figure(figsize=(8, 5))
plt.loglog(I_values, P_values, color='black')

ax = plt.gca()  # Get current axis

# Set a plain formatter that removes scientific notation
ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
ax.ticklabel_format(style='plain', axis='y')

# Explicitly set the y-axis label format to avoid scientific notation
ax.yaxis.set_minor_formatter(ticker.NullFormatter())  # Remove minor tick labels
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f"))  # Force integer formatting

# Ensure no offset text appears (removes the 2×10³)
ax.yaxis.get_offset_text().set_visible(False)

plt.axvline(time_balance_point, linestyle='--', color='red', alpha=0.6)
plt.axvline(energy_balance_point, linestyle='--', color='blue', alpha=0.6)
y = (1 + (energy_balance_point / time_balance_point)) * pi_flop / 10e2
plt.axhline(y, linestyle='--', color='black', alpha=0.6)

xticks = [30, 94]
plt.xticks(xticks, [r"$B_{\tau}$", r"$B_{\epsilon}$"], fontsize=15)
plt.yticks([y], [r"$y_{max}$"], fontsize=15)

plt.xlabel('Operational Intensity (Flop/Byte)', fontsize=12)
plt.ylabel(f'Watt', fontsize=12)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
plt.savefig("./DummyRoofline/dummyPowerline.pdf")