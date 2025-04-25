import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
for axis in [plt.gca().xaxis, plt.gca().yaxis]:
    axis.set_major_formatter(ScalarFormatter())
    axis.set_minor_formatter(ScalarFormatter())

I_values = np.logspace(np.log2(0.5), np.log2(256), 200, base=2)

# style and label values
filename = "Step-48"
W = 145_277_256_573 + 14_294_501_283
print(W / 650)
Q = 983_699_260
labels = ["2 cores", "4 cores", "8 cores", "12 cores", "16 cores", "20 cores", "24 cores", "28 cores", "32 cores"]
colors = ["#aaffc3", "#3cb44b", "#ffe119", "#0082c8", "#ff8c00", "#911eb4", "#46f0f0", "#a52a2a", "red"]
policies = ["PCoreFirst", "ECoreFirst", "Balanced"]
power_caps = ["50 W", "75 W", "100 W", "175 W", "253 W"]
num_cores = [1, 0, 2, 0, 4, 0, 6, 0, 8, 0, 8, 4, 8, 8, 8, 12, 8, 16,  # PCoreFirst
             0, 2, 0, 4, 0, 8, 0, 12, 0, 16, 2, 16, 4, 16, 6, 16, 8, 16,   # ECoreFirst
             0, 1, 1, 2, 2, 4, 3, 6, 4, 8, 5, 10, 6, 12, 7, 14, 8, 16]   # Balanced
legend = True

# TIME values
datasetPowerCapping = np.load(f"./Data/{filename}/datasetPowerCapping.npy", allow_pickle=True)
absolute_duration_time_dataset = datasetPowerCapping[0]
max_flops_time = 0
memory_bandwidth = 3.181735e10 #Byte/s
tau_flop = 0
tau_mem = 1 / memory_bandwidth #s/Byte
time_balance_point = 0

# ENERGY values
# ENERGY values
absolute_energy_consumption_dataset = datasetPowerCapping[2]
pi0 = 3.07                                                                # idle power in Joule
epsilon_mem = ((158.93 - pi0 * 1.19462) * 0.101167) / 32e8 # STEAM benchmark
max_flops_energy = (39164876476007 * 16) / 52516.83        # GEMM benchmark
epsilon_flop = 1 / max_flops_energy
energy_balance_point = epsilon_mem / epsilon_flop

constant_energy_per_flop = 0
actual_energy_per_flop = 0
constant_flop_energy_efficiency = 0
effective_energy_balance = 0


def calculateParameters(num_pcores, num_ecores, pcore_freq, ecore_freq):
    # TIME values
    max_flops_time = num_pcores * pcore_freq * 16 + num_ecores * ecore_freq * 4  # GFlops/s
    max_flops_time *= 10e8   # convert to Flops/s
    tau_flop = 1 / max_flops_time   # s/Flop
    time_balance_point = tau_mem / tau_flop  # Flop/Byte

    # ENERGY values
    constant_energy_per_flop = pi0 * tau_flop
    actual_energy_per_flop = epsilon_flop + constant_energy_per_flop
    constant_flop_energy_efficiency = epsilon_flop / actual_energy_per_flop
    effective_energy_balance = constant_flop_energy_efficiency * energy_balance_point
    effective_energy_balance += (1 - constant_flop_energy_efficiency) * (np.maximum(0, time_balance_point - I_values))

    return max_flops_time, tau_flop, time_balance_point, constant_energy_per_flop, actual_energy_per_flop, constant_flop_energy_efficiency, effective_energy_balance

def plotPointTime(W, Q, T, color):
    OI = W / Q
    performance = (W / T) / 1e9 # GFlop/s
    plt.scatter(OI, performance, color=color, marker="o", s=100, edgecolors='black', linewidths=0, zorder=10, alpha=0.8)

def plotPointEnergy(W, Q, E, color):
    OI = W / Q
    performance = (W / E) / 1e6    # MFlop/J
    plt.scatter(OI, performance, color=color, marker="o", s=100, edgecolors='black', linewidths=0, zorder=10, alpha=0.8)

# Plots for TIME
"""
for i in range(3):
    for j in range(5):
        plt.figure(figsize=(8, 10), dpi=120)
        for k in range(9):
            # ROOFLINE
            max_flops_time, tau_flop, time_balance_point, constant_energy_per_flop, actual_energy_per_flop, constant_flop_energy_efficiency, effective_energy_balance = calculateParameters(num_cores[i * 9 * 2 + k * 2], num_cores[i * 9 * 2 + k * 2 + 1], 5.5, 4.3)

            P_values = np.minimum(max_flops_time, I_values * memory_bandwidth) / 1e9  # GFLOP/s
            if legend:
                plt.loglog(I_values, P_values, label=f"#Cores - " + r"$P_{max}$" +" - " + r"$B_{\tau}$", color="white", linewidth=0)  # plot legend first line
                legend = False
            plt.loglog(I_values, P_values, label=f"{labels[k]} - {(max_flops_time / 10e8):.1f} GFLOP/s - {time_balance_point:.1f} FLOP/Byte", color=colors[k], linewidth=5)
            
            plt.axvline(time_balance_point, linestyle='--', color=colors[k], alpha=0.5, linewidth=2)

            plotPointTime(W, Q, absolute_duration_time_dataset[i, j, k], colors[k])

        xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256]
        yticks = [1, 5, 10, 20, 50, 100, 200, 500, 750, 1000]
        plt.xticks(xticks, [f"{x:.1f}" for x in xticks], fontsize=16)
        plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=16)

        plt.xlabel('Operational Intensity (Flop/Byte)', fontsize=22)
        plt.ylabel('GFLOP/s', fontsize=22)
        plt.legend(fontsize=15,
                       loc="upper center",
                       bbox_to_anchor=(0.5, -0.12),
                       ncol=1,
                       framealpha=0.5)
        plt.grid(True, which='both', linestyle=':', linewidth=0.3, alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(f"./Plots/{filename}/PowerCapping/{policies[i]}/Roofline/{power_caps[j]}.pdf")
        legend = True
"""

# Plots for ENERGY
for i in range(3):
    for j in range(5):
        plt.figure(figsize=(8, 8), dpi=120)
        for k in range(9):
            # ARCHLINE
            max_flops_time, tau_flop, time_balance_point, constant_energy_per_flop, actual_energy_per_flop, constant_flop_energy_efficiency, effective_energy_balance = calculateParameters(num_cores[i * 9 * 2 + k * 2], num_cores[i * 9 * 2 + k * 2 + 1], 5.5, 4.3)

            P_values = (1 / (1 + effective_energy_balance / I_values)) * max_flops_energy / 1e6 # MFLOP/J
            
            plt.loglog(I_values, P_values, label=f"{labels[k]}", color=colors[k], linewidth=3)
            
            plt.axvline(energy_balance_point, linestyle='--', color="blue", alpha=0.2, linewidth=2)

            plotPointEnergy(W, Q, absolute_energy_consumption_dataset[i, j, k], colors[k])

        xticks = [0.2, 0.5, 1, 2, 4, 8, 16, 32, 64, 128]
        yticks = [10, 20, 100, 200, 500, 1000, 2000, 5000, max_flops_energy / 1e6]
        plt.xticks(xticks, [f"{x:.1f}" for x in xticks], fontsize=16)
        plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=16)

        plt.xlabel('Operational Intensity (Flop/Byte)', fontsize=22)
        plt.ylabel('MFLOP/Joule', fontsize=22)
        plt.legend(fontsize=15,
                       loc="upper center",
                       bbox_to_anchor=(0.5, -0.12),
                       ncol=3,
                       framealpha=0.5)
        plt.grid(True, which='both', linestyle=':', linewidth=0.3, alpha=0.5)
        
        plt.tight_layout()
        plt.text(energy_balance_point * 1.1, 200, f'{energy_balance_point:.1f}', color="blue", fontsize=18)
        plt.savefig(f"./Plots/{filename}/PowerCapping/{policies[i]}/Archline/{power_caps[j]}.pdf")
        legend = True