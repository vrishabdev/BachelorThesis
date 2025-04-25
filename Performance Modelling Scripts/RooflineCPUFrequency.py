import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
for axis in [plt.gca().xaxis, plt.gca().yaxis]:
    axis.set_major_formatter(ScalarFormatter())
    axis.set_minor_formatter(ScalarFormatter())

I_values = np.logspace(np.log2(0.5), np.log2(128), 200, base=2)

# style and label values
filename = "Step-22"
W = 1_242_069_784 + 2 * 231_553_318
Q = 1_888_141_301
frequencies = [0.8, 1.3, 1.8, 2.3, 2.8, 3.3, 3.8, 4.3, 4.8, 5.3, 5.5]
labels = ["0.8 GHz", "1.3 GHz", "1.8 GHz", "2.3 GHz", "2.8 GHz", "3.3 GHz", "3.8 GHz", "4.3 GHz", "4.8 GHz", "5.3 GHz", "5.5 GHz"]
colors = ["#aaffc3", "#3cb44b", "#ffe119", "#0082c8", "#ff8c00", "#911eb4", "#46f0f0", "blue", "#ff88ff", "#616161", "blue"]
power_caps = ["50 W", "75 W", "100 W", "175 W", "253 W"]
core_type = ["PCoreScaling", "ECoreScaling"]
num_freq = [11, 8]
legend = True

# TIME values
absolute_duration_time_dataset = np.load(f"./Data/{filename}/datasetCPUFrequency.npy", allow_pickle=True).item()["P"]["absolute_duration_time"]
max_flops_time = 0
memory_bandwidth = 3.181735e10 #Byte/s
tau_flop = 0
tau_mem = 1 / memory_bandwidth #s/Byte
time_balance_point = 0

# ENERGY values
absolute_energy_consumption_dataset = np.load(f"./Data/{filename}/datasetCPUFrequency.npy", allow_pickle=True).item()["P"]["absolute_energy_consumption"]
pi0 = 3.07 # idle power in Joule
epsilon_mem = ((158.93 - pi0 * 1.19462) * 0.101167) / 32e8 # STEAM benchmark
max_flops_energy = (39164876476007 * 16) / 52516.83        # GEMM benchmark
epsilon_flop = 1 / max_flops_energy
energy_balance_point = epsilon_mem / epsilon_flop

constant_energy_per_flop = 0
actual_energy_per_flop = 0
constant_flop_energy_efficiency = 0
effective_energy_balance = 0

def calculateParameters(num_pcores, num_ecores, pcore_freq, ecore_freq, index):
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
for i in range(2):
    for j in range(5):
        plt.figure(figsize=(8, 10), dpi=120)
        for k in range(num_freq[i]):
            # ROOFLINE
            if i == 0:
                # DON'T FORGET TO SET THE #CORES AND FREQUENCY
                max_flops_time, tau_flop, time_balance_point, constant_energy_per_flop, actual_energy_per_flop, constant_flop_energy_efficiency, effective_energy_balance = calculateParameters(8, 16, frequencies[k], 4.3, 0)
            else:
                # DON'T FORGET TO SET THE #CORES AND FREQUENCY
                max_flops_time, tau_flop, time_balance_point, constant_energy_per_flop, actual_energy_per_flop, constant_flop_energy_efficiency, effective_energy_balance = calculateParameters(8, 16, 5.5, frequencies[k], 0)

            P_values = np.minimum(max_flops_time, I_values * memory_bandwidth) / 1e9  # GFLOP/s
            if legend:
                if i == 0:
                    plt.loglog(I_values, P_values, label=f"#cores - P-Core Freq - E-Core Freq - " + r"$P_{max}$" + " - " + r"$B_{\tau}$", color="white", linewidth=0) # plot legend first line
                else:
                    plt.loglog(I_values, P_values, label=f"#cores - P-Core Freq - E-Core Freq - " + r"$P_{max}$" + " - " + r"$B_{\tau}$", color="white", linewidth=0)
                legend = False
            if i == 0:
                plt.loglog(I_values, P_values, label=f"32 cores - {labels[k]} - 4.3 GHz - {(max_flops_time / 10e8):.0f} GFLOP/s - {time_balance_point:.1f} FLOP/Byte", color=colors[k], linewidth=5)
            else:
                plt.loglog(I_values, P_values, label=f"32 cores - 5.5 GHz - {labels[k]} - {(max_flops_time / 10e8):.0f} GFLOP/s - {time_balance_point:.1f} FLOP/Byte", color=colors[k], linewidth=5)

            plt.axvline(time_balance_point, linestyle='--', color=colors[k], alpha=0.5, linewidth=2)

            plotPointTime(W, Q, absolute_duration_time_dataset[j, k], colors[k])

        xticks = [0.2, 0.5, 2, 8, 16, 32, 64]
        yticks = [0.5, 1, 5, 10, 50, 100, 200, 500, 1000]
        plt.xticks(xticks, [f"{x:.1f}" for x in xticks], fontsize=16)
        plt.yticks(yticks, [f"{y:.1f}" for y in yticks], fontsize=16)

        plt.xlabel('Operational Intensity (Flop/Byte)', fontsize=22)
        plt.ylabel('GFLOP/s', fontsize=22)
        plt.legend(fontsize=15,
                       loc="upper center",
                       bbox_to_anchor=(0.5, -0.14),
                       ncol=1,
                       framealpha=0.5)
        plt.grid(True, which='both', linestyle=':', linewidth=0.3, alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(f"./Plots/{filename}/CPUFrequency/{core_type[i]}/Roofline/{power_caps[j]}.png")
        legend = True
    
    absolute_duration_time_dataset = np.load(f"./Data/{filename}/datasetCPUFrequency.npy", allow_pickle=True).item()["E"]["absolute_duration_time"]
"""

# Plots for ENERGY
for i in range(2):
    for j in range(5):
        plt.figure(figsize=(8, 10), dpi=120)
        for k in range(num_freq[i]):
            # ROOFLINE
            if i == 0:
                # DON'T FORGET TO SET THE #CORES AND FREQUENCY
                max_flops_time, tau_flop, time_balance_point, constant_energy_per_flop, actual_energy_per_flop, constant_flop_energy_efficiency, effective_energy_balance = calculateParameters(1, 0, frequencies[k], 4.3, 0)
            else:
                # DON'T FORGET TO SET THE #CORES AND FREQUENCY
                max_flops_time, tau_flop, time_balance_point, constant_energy_per_flop, actual_energy_per_flop, constant_flop_energy_efficiency, effective_energy_balance = calculateParameters(0, 1, 5.5, frequencies[k], 0)

            P_values = (1 / (1 + effective_energy_balance / I_values)) * max_flops_energy / 1e6 # MFLOP/J
            if legend:
                if i == 0:
                    plt.loglog(I_values, P_values, label=f"#P-cores - P-Core Freq", color="white", linewidth=0) # plot legend first line
                else:
                    plt.loglog(I_values, P_values, label=f"#E-cores - E-Core Freq", color="white", linewidth=0)
                legend = False
            if i == 0:
                plt.loglog(I_values, P_values, label=f"1 cores - {labels[k]}", color=colors[k], linewidth=2)
            else:
                plt.loglog(I_values, P_values, label=f"1 cores - {labels[k]}", color=colors[k], linewidth=2)

            plt.axvline(energy_balance_point, linestyle='--', color="blue", alpha=0.2, linewidth=1)

            plotPointEnergy(W, Q, absolute_energy_consumption_dataset[j, k], colors[k])

        xticks = [0.5, 1, 2, 8, 16, 32, 64, 128]
        yticks = [5, 10, 20, 50, 100, 200, 500, 1000, 5000, max_flops_energy / 1e6]
        plt.xticks(xticks, [f"{x:.1f}" for x in xticks], fontsize=16)
        plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=16)

        plt.xlabel('Operational Intensity (Flop/Byte)', fontsize=22)
        plt.ylabel('MFLOP/Joule', fontsize=22)
        plt.legend(fontsize=15,
                       loc="upper center",
                       bbox_to_anchor=(0.5, -0.14),
                       ncol=1,
                       framealpha=0.5)
        plt.grid(True, which='both', linestyle=':', linewidth=0.3, alpha=0.5)
        
        plt.tight_layout()
        plt.text(energy_balance_point * 1.1, 200, f'{energy_balance_point:.1f}', color="blue", fontsize=18)
        plt.savefig(f"./Plots/{filename}/CPUFrequency/{core_type[i]}/Archline/{power_caps[j]}.pdf")
        legend = True
    
    absolute_energy_consumption_dataset = np.load(f"./Data/{filename}/datasetCPUFrequency.npy", allow_pickle=True).item()["E"]["absolute_energy_consumption"]

