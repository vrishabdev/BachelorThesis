from fabric import Connection
import re
import numpy as np
import PlotData as plot
import CreateTable as table

jump_host = f"vit@login.caps.in.tum.de"
dest_host = f"vit@regale.caps.in.tum.de"

jump_conn = Connection(jump_host)
dest_conn = Connection(dest_host, gateway=jump_conn)

# dataset: 3 graphs(allocation policy), 5 fuctions(PowerCap) per graph, 9 data points(core allocation) per PowerCap
absolute_duration_time_dataset = np.zeros((3, 5, 9), dtype=float)
relative_duration_time_dataset = np.zeros((3, 5, 9) , dtype=float)
absolute_energy_consumption_dataset = np.zeros((3, 5, 9), dtype=float)
relative_energy_consumption_dataset = np.zeros((3, 5, 9), dtype=float)
absolute_edp_dataset = np.zeros((3, 5, 9), dtype=float)
relative_edp_dataset = np.zeros((3, 5, 9), dtype=float)
relative_ipc_dataset = np.zeros((3, 5, 9), dtype=float)

filename = "Step-48"
path = f"/u/home/vit/dealii/examples/{filename.lower()}/Evaluations/PowerCapping/"
directories = ["50Watt/", "75Watt/", "100Watt/", "175Watt/", "253Watt/"]
sub_directories = ["PCoreFirst/", "ECoreFirst/", "Balanced/"]
sub_directories_energy = ["PCoreFirstEnergy/", "ECoreFirstEnergy/", "BalancedEnergy/"]
num_cores = [2, 4, 8, 12, 16, 20, 24, 28, 32]

def extract_value(pattern, content):
    match = re.search(pattern, content)
    return float(match.group(1)) if match else 0.0

# extract absolute values
for i in range(3):
    for j in range(5):
        print(f"{directories[j]}{sub_directories[i]}")
        with dest_conn, jump_conn:
            result = dest_conn.run(f"ls -tr {path}{directories[j]}{sub_directories[i]}*.csv", hide=True)
            csv_files = result.stdout.strip().split("\n")
            for k in range(9):
                file_content = dest_conn.run(f'cat "{csv_files[k]}"', hide=True).stdout

                # absolute_duration_time in seconds
                absolute_duration_time_dataset[i, j, k] = extract_value(r'(\d+),ns,duration_time', file_content) / 1_000_000_000

                # absolute_ipc
                instructions = extract_value(r'(\d+),,cpu_atom/instructions/', file_content)
                instructions += extract_value(r'(\d+),,cpu_core/instructions/', file_content)
                cycles = extract_value(r'(\d+),,cpu_atom/cycles/', file_content);
                cycles += extract_value(r'(\d+),,cpu_core/cycles/', file_content)
                relative_ipc_dataset[i, j, k] = instructions / cycles

                # values for roofline model
                # TODO

            result = dest_conn.run(f"ls -tr {path}{directories[j]}{sub_directories_energy[i]}*.csv", hide=True)
            csv_files = result.stdout.strip().split("\n")
            for k in range(9):
                file_content = dest_conn.run(f'cat "{csv_files[k]}"', hide=True).stdout
                
                # absolute_energy_consumption
                absolute_energy_consumption_dataset[i, j, k] = extract_value(r'(\d+),\d+,Joules,power/energy-pkg/', file_content)

                # absolute_edp
                absolute_edp_dataset[i, j, k] = absolute_duration_time_dataset[i, j, k] * absolute_energy_consumption_dataset[i, j, k]

# calculate relative values
datasets = {
    "duration_time": (absolute_duration_time_dataset, relative_duration_time_dataset),
    "energy_consumption": (absolute_energy_consumption_dataset, relative_energy_consumption_dataset),
    "edp": (absolute_edp_dataset, relative_edp_dataset),
    "ipc": (relative_ipc_dataset, relative_ipc_dataset),
}
for i in range(3):
    for j in range(5):
        for key, (absolute, relative) in datasets.items():
            base_value = absolute[i, 4, 8]          # all resources allocated
            if base_value != 0:
                if key == "ipc":
                    relative[i, j, :] = base_value / relative[i, j, :]
                else:
                    relative[i, j, :] = absolute[i, j, :] / base_value

# save data
dataset = [absolute_duration_time_dataset, relative_duration_time_dataset,
        absolute_energy_consumption_dataset, relative_energy_consumption_dataset,
        absolute_edp_dataset, relative_edp_dataset, relative_ipc_dataset]
np.save(f"./Data/{filename}/datasetPowerCapping.npy", dataset)

# plot data
# plot.plotPowerCapping(dataset, "Step-48")

# create table
# table.createTable(absolute_duration_time_dataset, absolute_energy_consumption_dataset, filename)