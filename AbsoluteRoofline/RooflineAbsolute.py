import numpy as np
import matplotlib.pyplot as plt
from fractions import Fraction

I_values = np.logspace(np.log2(0.2), np.log2(1024), 200, base=2)

# TIME values
max_flops_time = 979.2e9 #Flop/s
memory_bandwidth = 31.95e9 #Byte/s    should I use 89.6e9 the theoretical value? time balance point would be 10.9
tau_flop = 1 / max_flops_time #s/Flop
tau_mem = 1 / memory_bandwidth #s/Byte
time_balance_point = tau_mem / tau_flop #Flop/Byte

# Roofline
P_values = np.minimum(max_flops_time, I_values * memory_bandwidth) / 1e9  # GFLOP/s

plt.figure(figsize=(8, 7))
plt.loglog(I_values, P_values, color='red', linewidth=5)

plt.axvline(time_balance_point, linestyle='--', color='red', alpha=0.5, linewidth=2)
plt.text(time_balance_point, 1300, f'{time_balance_point:.1f}', color='red', fontsize=18)

xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
yticks = [1, 5, 10, 20, 50, 100, 200, 500, max_flops_time / 1e9]
plt.xticks(xticks, [f"{x:.0f}" for x in xticks], fontsize=16)
plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=16)

plt.xlabel('Operational Intensity (Flop/Byte)', fontsize=22)
plt.ylabel('GFLOP/s', fontsize=22)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# plot values for the roofline
def plotRoofline(W, Q, T, benchmark):
    OI = W / Q
    P_time = (W / T) / 1e9 # GFlop/s
    plt.scatter(OI, P_time, color='red', label=benchmark, s=6)
    plt.text(OI * 1.1, P_time, benchmark, fontsize=10)

plt.savefig("./AbsoluteRoofline/rooflineAbsolute.pdf")


# ENERGY values
pi0 = 3.07 # idle power in Joule

#max_flops_energy = 2.664e11 / 11.88   # Flop/Joule      of the mp_linpack benchmark
max_flops_energy = (39164876476007 * 16) / 52516.83 #156.91#633.74214e9 / 120.69         # GEMM benchmark, double-precision
epsilon_mem = ((158.93 - pi0 * 1.19462) * 0.101167) / 32e8      # Joule/Byte      of the STREAM benchmark
epsilon_flop = 1 / max_flops_energy        # Joule/Flop      of the mp_linpack benchmark
energy_balance_point = epsilon_mem / epsilon_flop          # Flop/Joule

constant_energy_per_flop = pi0 * tau_flop
actual_energy_per_flop = epsilon_flop + constant_energy_per_flop
constant_flop_energy_efficiency = epsilon_flop / actual_energy_per_flop
effective_energy_balance = constant_flop_energy_efficiency * energy_balance_point
effective_energy_balance += (1 - constant_flop_energy_efficiency) * (np.maximum(0, time_balance_point - I_values))

# Archline
P_values = (1 / (1 + effective_energy_balance / I_values)) * max_flops_energy / 1e6 # MFLOP/J

plt.figure(figsize=(10, 7))
plt.loglog(I_values, P_values, color='blue', linewidth=5)

plt.axvline(energy_balance_point, linestyle='--', color='blue', alpha=0.6, linewidth=2)
plt.text(energy_balance_point * 1.2, 16000, f'{energy_balance_point:.1f}', color='blue', fontsize=18)

xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
yticks = [10, 50, 100, 200, 500, 1000, 5000, max_flops_energy / 1e6]
plt.xticks(xticks, [f"{x:.0f}" for x in xticks], fontsize=16)
plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=16)

plt.xlabel('Operational Intensity (Flop/Byte)', fontsize=22)
plt.ylabel('MFLOP/J', fontsize=22)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

def plotArchline(W, Q, E, benchmark):
    OI = W / Q
    P_energy = (W / E) / 1e6    # MFlop/J
    plt.scatter(OI, P_energy, color='blue', label=benchmark, s=6)
    plt.text(OI * 1.1, P_energy, benchmark, fontsize=10)

plotArchline(145_277_256_573 + 14_294_501_283, 1030886522, 658.25, "Step-48") #983_699_260
# plotArchline(2_938_329_625 +  2 * 287_381_972, 13_793_476_301, 400.77, "Step-37")
# plotArchline(1_242_069_784 + 2 * 231_553_318, 1_888_141_301, 72.71, "Step-22")
# plotArchline(430_487_020_879 + 2 * 56_346_215_064, 854_173_536_829, 4739.46, "Step-56")
# plotArchline(3_172_665_173 + 2 * 3_321_644_899, 5_983_805_276, 290, "Step-23")

plt.savefig("./AbsoluteRoofline/archlineAbsolute.pdf")

# POWER values
pi_flop = epsilon_flop / tau_flop

# Powerline
temp = pi_flop / constant_flop_energy_efficiency
temp2 = np.minimum(I_values, time_balance_point) / time_balance_point
temp2 += (effective_energy_balance / np.maximum(I_values, time_balance_point))
P_values = (temp * temp2)

plt.figure(figsize=(8, 6))
plt.loglog(I_values, P_values, color='black')

plt.axvline(time_balance_point, linestyle='--', color='red', alpha=0.6)
plt.text(time_balance_point * 1.2, 60, f'{time_balance_point:.1f}', color='red')

plt.axvline(energy_balance_point, linestyle='--', color='blue', alpha=0.6)
plt.text(energy_balance_point * 1.2, 60, f'{energy_balance_point:.1f}', color='blue')

plt.axhline(pi_flop, linestyle='--', color='black', alpha=0.6)
plt.text(x=1, y=pi_flop*1.05, s=f'{pi_flop:.0f} W', color='black')

y = (energy_balance_point / time_balance_point) * pi_flop
plt.axhline(y, linestyle='--', color='black', alpha=0.6)
plt.text(x=1, y=y*1.05, s=f'{y:.0f} W', color='black')

y = (1 + (energy_balance_point / time_balance_point)) * pi_flop
plt.axhline(y, linestyle='--', color='black', alpha=0.6)
plt.text(x=3, y=y*1.05, s=f'{y:.0f} W', color='black')

xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
yticks = [50, 100, 500, 1000, 2000]
plt.xticks(xticks, [f"{x:.0f}" for x in xticks], fontsize=6)
plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=6)

plt.xlabel('Operational Intensity (Flop/Byte)')
plt.ylabel(f'Watt')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

def plotPowerline(W, Q, T, E, benchmark):
    OI = W / Q
    power = E / T
    plt.scatter(OI, power, color='black', label=benchmark, s=6)
    plt.text(OI * 1.1, power, benchmark, fontsize=10)

plotPowerline(145_277_256_573 + 14_294_501_283, 983_699_260, 5.96766894, 658.25, "Step-48")

plt.savefig("./AbsoluteRoofline/powerlineAbsolute.pdf")