import numpy as np
import matplotlib.pyplot as plt
from fractions import Fraction

I_values = np.logspace(np.log2(0.5), np.log2(8192), 200, base=2)

# TIME values
max_flops_time = 9.792e11 #Flop/s
memory_bandwidth = 3.195e10 #Byte/s
tau_flop = 1 / max_flops_time #s/Flop
tau_mem = 1 / memory_bandwidth #s/Byte
time_balance_point = tau_mem / tau_flop #Flop/Byte

# Roofline
P_values = np.minimum(max_flops_time, I_values * memory_bandwidth) / 1e9  # GFLOP/s

plt.figure(figsize=(8, 6))
plt.loglog(I_values, P_values, label='Roofline (GFLOP/s)', color='red')

plt.axvline(time_balance_point, linestyle='--', color='red', alpha=0.6)
plt.text(time_balance_point * 1.2, 20, f'{time_balance_point:.1f}', color='red')

xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
yticks = [1, 5, 10, 20, 50, 100, 200, 500, max_flops_time / 1e9]
plt.xticks(xticks, [f"{x:.0f}" for x in xticks], fontsize=6)
plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=6)

plt.xlabel('Operational Intensity (Flop/Byte)')
plt.ylabel('GFLOP/s')
plt.title('Roofline Model (Intel Core i9-13900K Processor)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# plot values for the roofline
def plotRoofline(W, Q, T, benchmark):
    OI = W / Q
    P_time = (W / T) / 1e9 # GFlop/s
    plt.scatter(OI, P_time, color='red', label=benchmark, s=6)
    plt.text(OI * 1.1, P_time, benchmark, fontsize=10)

plotRoofline(146_181_658_218 + 14_411_973_290, (11_273_513 + 5_571_360) * 64, 5.7751, "Step-48")
plotRoofline(165_367_458 + (79_758_605 * 2), (822_679 + 260_175) * 64, 0.226, "Step-6")
plotRoofline(3_060_227_507 + (3_243_934_680 * 2), (59_576_674 + 35_191_217) * 64, 14.653, "Step-23")
plotRoofline(22_393_784 + (8_293_241 * 2), (689_288 + 191_455) * 64, 0.08078, "Step-61")

plotRoofline(1_659_750_970 + 24_590_181, (4_382_992 + 1_066_678) * 64, 0.84067, "CG-A")
plotRoofline(54_613_840_828 + 588_243_691, (2_277_523_624 + 11_692_672) * 64, 16.55, "CG-B")

plt.savefig("rooflineAbsolute.png")


# ENERGY values
pi0 = 3.71 # idle power in Joule 
max_power = 253 # Watt

max_flops_energy = 2.72597e11 / (15.35 - pi0 * 0.68614)    # Flop/Joule      of the mp_linpack benchmark
epsilon_mem = (36.47 - pi0 * 0.29946) / 8e8                # Joule/Byte      of the STREAM benchmark
epsilon_flop = (15.35 - pi0 * 0.68614) / 2.72597e11        # Joule/Flop      of the mp_linpack benchmark
energy_balance_point = epsilon_mem / epsilon_flop          # Flop/Joule

constant_energy_per_flop = pi0 * tau_flop
actual_energy_per_flop = epsilon_flop + constant_energy_per_flop
constant_flop_energy_efficiency = epsilon_flop / actual_energy_per_flop
effective_energy_balance = constant_flop_energy_efficiency * energy_balance_point
effective_energy_balance += (1 - constant_flop_energy_efficiency) * (np.maximum(0, time_balance_point - I_values))

# Archline
P_values = (1 / (1 + effective_energy_balance / I_values)) * max_flops_energy / 1e6 # MFLOP/J

plt.figure(figsize=(8, 6))
plt.loglog(I_values, P_values, label='Archline (MFLOP/J)', color='blue')

plt.axvline(energy_balance_point, linestyle='--', color='blue', alpha=0.6)
plt.text(energy_balance_point * 1.2, 15, f'{energy_balance_point:.1f}', color='blue')

xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
yticks = [10, 50, 100, 500, 1000, 5000, 10000, 15000, 20000, max_flops_energy / 1e6]
plt.xticks(xticks, [f"{x:.0f}" for x in xticks], fontsize=6)
plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=6)

plt.xlabel('Operational Intensity (Flop/Byte)')
plt.ylabel('MFLOP/J')
plt.title('Archline Model (Intel Core i9-13900K Processor)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

def plotArchline(W, Q, E, benchmark):
    OI = W / Q
    P_energy = (W / E) / 1e6    # MFlop/J
    plt.scatter(OI, P_energy, color='blue', label=benchmark, s=6)
    plt.text(OI * 1.1, P_energy, benchmark, fontsize=10)

plotArchline(146_181_658_218 + 14_411_973_290, (11_273_513 + 5_571_360) * 64, 634.03, "Step-48")
plotArchline(165_367_458 + (79_758_605 * 2), (822_679 + 260_175) * 64, 29.11, "Step-6")
plotArchline(3_060_227_507 + (3_243_934_680 * 2), (59_576_674 + 35_191_217) * 64, 285.19, "Step-23")
plotArchline(22_393_784 + (8_293_241 * 2), (689_288 + 191_455) * 64, 16.82, "Step-61")

plotArchline(1_659_750_970 + 24_590_181, (4_382_992 + 1_066_678) * 64, 19.04, "CG-A")
plotArchline(54_613_840_828 + 588_243_691, (2_277_523_624 + 11_692_672) * 64, 701.09, "CG-B")

plt.savefig("archlineAbsolute.png")

# POWER values
pi_flop = epsilon_flop / tau_flop

# Powerline
temp = pi_flop / constant_flop_energy_efficiency
temp2 = np.minimum(I_values, time_balance_point) / time_balance_point
temp2 += (effective_energy_balance / np.maximum(I_values, time_balance_point))
P_values = (temp * temp2)

plt.figure(figsize=(8, 6))
plt.loglog(I_values, P_values, label='Powerline (Watt)', color='black')

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
plt.title('Powerline Model (Intel Core i9-13900K Processor)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

def plotPowerline(W, Q, T, E, benchmark):
    OI = W / Q
    power = E / T
    plt.scatter(OI, power, color='black', label=benchmark, s=6)
    plt.text(OI * 1.1, power, benchmark, fontsize=10)

plotPowerline(146_181_658_218 + 14_411_973_290, (11_273_513 + 5_571_360) * 64, 5.7401, 634.03, "Step-48")

plt.savefig("powerlineAbsolute.png")