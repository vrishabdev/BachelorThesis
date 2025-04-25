from fabric import Connection
import re
import numpy as np
import PlotData as plot
import CreateTable as table

jump_host = f"vit@login.caps.in.tum.de"
dest_host = f"vit@regale.caps.in.tum.de"

jump_conn = Connection(jump_host)
dest_conn = Connection(dest_host, gateway=jump_conn)

# Configuration
filename = "Step-23"
path = f"/u/home/vit/dealii/examples/{filename.lower()}/Evaluations/CPUFrequency/"
directories = ["50Watt/", "75Watt/", "100Watt/", "175Watt/", "253Watt/"]

configurations = {
    "P": {"sub_dirs": ["PCoreScaling/", "PCoreScalingEnergy/"], "num_freq": 11},
    "E": {"sub_dirs": ["ECoreScaling/", "ECoreScalingEnergy/"], "num_freq": 8}
}

# Dataset initialization
datasets = {}
for core_type, config in configurations.items():
    datasets[core_type] = {
        "absolute_duration_time": np.zeros((5, config["num_freq"]), dtype=float),
        "relative_duration_time": np.zeros((5, config["num_freq"]), dtype=float),
        "absolute_energy_consumption": np.zeros((5, config["num_freq"]), dtype=float),
        "relative_energy_consumption": np.zeros((5, config["num_freq"]), dtype=float),
        "absolute_edp": np.zeros((5, config["num_freq"]), dtype=float),
        "relative_edp": np.zeros((5, config["num_freq"]), dtype=float),
        "absolute_ipc": np.zeros((5, config["num_freq"]), dtype=float),
        "relative_ipc": np.zeros((5, config["num_freq"]), dtype=float),
        "W": np.zeros((5, config["num_freq"]), dtype=float), #flops
        "Q": np.zeros((5, config["num_freq"]), dtype=float), #mops
    }

def extract_value(pattern, content):
    match = re.search(pattern, content)
    if match:
        value_str = match.group(1).replace(",", ".")
        return float(value_str)
    return 0.0

def process_core_scaling(core_type):
    num_freq = configurations[core_type]["num_freq"]
    sub_dirs = configurations[core_type]["sub_dirs"]

    # Calculate absolute values
    for i in range(5):
        print(f"{directories[i]}")
        with dest_conn, jump_conn:
                result = dest_conn.run(f"ls -tr {path}{directories[i]}{sub_dirs[0]}*.csv", hide=True)
                csv_files = result.stdout.strip().split("\n")
                for j in range(num_freq):
                    file_content = dest_conn.run(f'cat "{csv_files[j]}"', hide=True).stdout

                    #absolute_duration_time in seconds
                    datasets[core_type]["absolute_duration_time"][i, j] = extract_value(r'(\d+),ns,duration_time', file_content) / float(1_000_000_000)

                    #absolute_ipc
                    instructions = extract_value(r'(\d+),,cpu_atom/instructions/', file_content)
                    instructions += extract_value(r'(\d+),,cpu_core/instructions/', file_content)
                    cycles = extract_value(r'(\d+),,cpu_atom/cycles/', file_content)
                    cycles += extract_value(r'(\d+),,cpu_core/cycles/', file_content)
                    datasets[core_type]["absolute_ipc"][i, j] = instructions / cycles

                    #W - flops
                    datasets[core_type]["W"][i, j] = extract_value(r'(\d+),,cpu_core/fp_arith_inst_retired.scalar_double/', file_content)
                    datasets[core_type]["W"][i, j] += extract_value(r'(\d+),,cpu_core/fp_arith_inst_retired.128b_packed_double/', file_content)

                    #Q - mops
                    datasets[core_type]["Q"][i, j] = extract_value(r'(\d+),,cpu_core/mem-stores/', file_content)
                    datasets[core_type]["Q"][i, j] += extract_value(r'(\d+),,cpu_atom/mem-stores/', file_content)
                    datasets[core_type]["Q"][i, j] += extract_value(r'(\d+),,cpu_core/mem-loads/', file_content)
                    datasets[core_type]["Q"][i, j] += extract_value(r'(\d+),,cpu_atom/mem-loads/', file_content)

                result = dest_conn.run(f"ls -tr {path}{directories[i]}{sub_dirs[1]}*.csv", hide=True)
                csv_files = result.stdout.strip().split("\n")
                for j in range(num_freq):
                    file_content = dest_conn.run(f'cat "{csv_files[j]}"', hide=True).stdout
                    
                    #absolute_energy_consumption
                    datasets[core_type]["absolute_energy_consumption"][i, j] = extract_value(r'(\d+,\d+),Joules,power/energy-pkg/', file_content)

                    #absolute_edp
                    datasets[core_type]["absolute_edp"][i, j] = datasets[core_type]["absolute_duration_time"][i, j] * datasets[core_type]["absolute_energy_consumption"][i, j]
    
    # Calculate realtive values
    relative_metrics = ["relative_duration_time", "relative_energy_consumption", "relative_edp", "relative_ipc"]
    absolute_metrics = ["absolute_duration_time", "absolute_energy_consumption", "absolute_edp", "absolute_ipc"]
    for i in range(5):
        for rel, abs in zip(relative_metrics, absolute_metrics):
            base_value = datasets[core_type][abs][4, num_freq - 1]    # all resources allocated
            if base_value != 0:
                if rel == "relative_ipc":
                    datasets[core_type][rel][i, :] = base_value / datasets[core_type][abs][i, :]
                else:
                    datasets[core_type][rel][i, :] = datasets[core_type][abs][i, :] / base_value


# Process both PCoreScaling and ECoreScaling
process_core_scaling("P")
process_core_scaling("E")

# Save data
np.save(f"./Data/{filename}/datasetCPUFrequency.npy", datasets)

# Plot the data
plot.plotCPUFrequency(datasets, filename)  

# Create tables
table.createTableFrequency(datasets["P"]["absolute_duration_time"], datasets["P"]["absolute_energy_consumption"], filename, configurations["P"]["num_freq"])
table.createTableFrequency(datasets["E"]["absolute_duration_time"], datasets["E"]["absolute_energy_consumption"], filename, configurations["E"]["num_freq"])