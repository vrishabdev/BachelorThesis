import matplotlib.pyplot as plt

metrics = ["absolute_duration_time", "relative_duration_time",
            "absolute_energy_consumption", "relative_energy_consumption",
            "absolute_edp", "relative_edp", "relative_ipc"]

yLabels = ["Absolute Duration Time in Seconds", "Relative Duration Time",
            "Absolute Energy Consumption in Joules", "Relative Energy Consumption",
            "Absolute EDP", "Relative EDP", "Relative IPC"]

power_caps = ["50Watt", "75Watt", "100Watt", "175Watt", "253Watt"]

colors = ["#4A90A2", "#4C9A81", "#7161EF", "#D08C60", "#B85042"]

num_cores = [2, 4, 8, 12, 16, 20, 24, 28, 32]

allocation_policies = ["PCoreFirst", "ECoreFirst", "Balanced"]

def plotCoreAllocation(dataset, filename):
    colors = ["red", "green", "blue"]
    for i in range(7):
        for j in range(3):
            plt.plot(num_cores, dataset[i][j], label=allocation_policies[j], color=colors[j], marker="o")
        
        plt.xlabel("Number of Cores")
        plt.ylabel(yLabels[i])
        plt.title(f"{filename}")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"./Plots/{filename}/CoreAllocation/{metrics[i]}.png")
        plt.close()

def plotPowerCapping(dataset, filename):
    # one graph for each policy
    for i, policy in enumerate(allocation_policies):
        plt.figure(figsize=(10, 6))
        # one graph for each metric
        for k, data in enumerate(dataset):
            for j, (power_cap, color) in enumerate(zip(power_caps, colors)):
                plt.plot(num_cores, data[i, j, :], label=power_cap, color=color, marker='o')
            
            plt.xlabel("Number of Cores")
            plt.ylabel(yLabels[k])
            plt.title(f"{filename} - {policy}")
            plt.legend()
            plt.grid(True)
            plt.savefig(f"./Plots/{filename}/PowerCapping/{policy}/{metrics[k]}.png")
            plt.close()

def plotCPUFrequency(datasets, filename):
    cpu_freqs = {
        "P": [0.8, 1.3, 1.8, 2.3, 2.8, 3.3, 3.8, 4.3, 4.8, 5.3, 5.5],
        "E": [0.8, 1.3, 1.8, 2.3, 2.8, 3.3, 3.8, 4.3]
    }
    # two graphs for each metric with 5 functions (power caps) each
    for metric_index, metric in enumerate(metrics):
        for core_type in ["P", "E"]:
            cpu_frequency = cpu_freqs[core_type]
            plt.figure(figsize=(8, 6))
            for i, (power_cap, color) in enumerate(zip(power_caps, colors)):
                plt.plot(cpu_frequency, datasets[core_type][metric][i, :], label=power_cap, color=color, marker='o')

            plt.xlabel(f"{core_type}-Core Frequency (GHz)")
            plt.ylabel(yLabels[metric_index])
            plt.title(f"{filename} - {core_type}Core Frequency Scaling")
            plt.legend()
            plt.grid(True)
            plt.savefig(f"./Plots/{filename}/CPUFrequency/{core_type}CoreScaling/{metric}.png")
            plt.close()