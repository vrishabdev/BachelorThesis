import matplotlib.pyplot as plt

metrics = ["absolute_duration_time", "relative_duration_time",
            "absolute_energy_consumption", "relative_energy_consumption",
            "absolute_edp", "relative_edp", "relative_ipc"]

yLabels = ["Duration Time in Seconds", "Relative Duration Time",
            "Energy Consumption in Joules", "Relative Energy Consumption",
            "EDP", "Relative EDP", "Relative IPC"]

power_caps = ["50 W", "75 W", "100 W", "175 W", "253 W"]

colors = ["#00A651", "#0073E6", "#A569BD", "#FFC300", "#FF5733"]

num_cores = [2, 4, 8, 12, 16, 20, 24, 28, 32]

allocation_policies = ["PCoreFirst", "ECoreFirst", "Balanced"]

def plotCoreAllocation(dataset, filename):
    colors = ["red", "green", "blue"]
    for i in range(7):
        for j in range(3):
            plt.plot(num_cores, dataset[i][j], label=allocation_policies[j], color=colors[j], marker="o")
        
        plt.xlabel("Number of Threads", fontsize=20)
        plt.ylabel(yLabels[i], fontsize=20)
        # plt.title(f"{filename}")
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.legend(fontsize=15, loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=5)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"./Plots/{filename}/CoreAllocation/{metrics[i]}.png")
        plt.close()

def plotPowerCapping(dataset, filename):
    # one graph for each policy
    for i, policy in enumerate(allocation_policies):
        # one graph for each metric
        for k, data in enumerate(dataset):
            plt.figure(figsize=(12, 8)) 
            for j, (power_cap, color) in enumerate(zip(power_caps, colors)):
                plt.plot(num_cores, data[i, j, :], 
                        label=power_cap, 
                        color=color, 
                        marker='o',
                        linewidth=5,  # Thicker lines
                        markersize=15)  # Larger markers
            
            plt.xlabel("Number of Threads", fontsize=24) 
            plt.ylabel(yLabels[k], fontsize=24)
            plt.xticks(fontsize=22)  
            plt.yticks(fontsize=22)
            plt.legend(fontsize=22,
                      loc="upper center",
                      bbox_to_anchor=(0.5, -0.2), 
                      ncol=5,
                      framealpha=0.5)
            
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"./Plots/{filename}/PowerCapping/{policy}/{metrics[k]}.pdf", 
                       bbox_inches='tight')
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
            plt.figure(figsize=(12, 8))
            for i, (power_cap, color) in enumerate(zip(power_caps, colors)):
                plt.plot(cpu_frequency, datasets.item()[core_type][metric][i, :],
                         label=power_cap,
                         color=color,
                         marker='o',
                         linewidth=5,
                         markersize=15)

            plt.xlabel(f"{core_type}-Core Frequency (GHz)", fontsize=24)
            plt.ylabel(yLabels[metric_index], fontsize=24)
            # plt.title(f"{filename} - {core_type}Core Frequency Scaling")
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)
            plt.legend(fontsize=22,
                       loc="upper center",
                       bbox_to_anchor=(0.5, -0.2),
                       ncol=5,
                       framealpha=0.5)
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"./Plots/{filename}/CPUFrequency/{core_type}CoreScaling/{metric}.pdf")
            plt.close()