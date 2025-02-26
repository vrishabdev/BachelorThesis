from fabric import Connection
import re
import PlotData as plot

jump_host = f"vit@login.caps.in.tum.de"
dest_host = f"vit@regale.caps.in.tum.de"

jump_conn = Connection(jump_host)
dest_conn = Connection(dest_host, gateway=jump_conn)

#dataset
absolute_duration_time_dataset = []
relative_duration_time_dataset = []
absolute_energy_consumption_dataset = []
relative_energy_consumption_dataset = []
absolute_edp_dataset = []
relative_edp_dataset = []
relative_ipc_dataset = []

path = "/u/home/vit/dealii/examples/step-37/Evaluations/"
directories = ["PCoreFirst", "ECoreFirst", "Balanced"]
directoriesEnergy = ["PCoreFirstEnergy", "ECoreFirstEnergy", "BalancedEnergy"]
for i in range(3):
    print(f"Reading directory: ${directories[i]}")
    
    #metrics
    absolute_duration_time = []
    relative_duration_time = []
    absolute_energy_consumption = []
    relative_energy_consumption = []
    absolute_edp = []
    relative_edp = []
    absolute_ipc = []
    relative_ipc = []

    with dest_conn, jump_conn:
        result = dest_conn.run(f"ls -tr {path}{directories[i]}/*.csv", hide=True)
        csv_files = result.stdout.strip().split("\n")
        for csv_file in csv_files:
            #print(f"Reading file: {csv_file}")
            file_content = dest_conn.run(f'cat "{csv_file}"', hide=True).stdout

            #absolute_duration_time
            match = re.search(r'(\d+),ns,duration_time', file_content)
            absolute_duration_time.append(float(match.group(1)) / 1_000_000_000)if match else absolute_duration_time.append(float(0))
            
            #absolute_ipc
            match = re.search(r'(\d+),,cpu_atom/instructions/', file_content)
            instructions = float(match.group(1)) if match else float(0)
            match = re.search(r'(\d+),,cpu_core/instructions/', file_content)
            instructions += float(match.group(1)) if match else float(0)
            
            match = re.search(r'(\d+),,cpu_atom/cycles/', file_content)
            cycles = float(match.group(1)) if match else float(0)
            match = re.search(r'(\d+),,cpu_core/cycles/', file_content)
            cycles += float(match.group(1)) if match else float(0)
            
            absolute_ipc.append(instructions / cycles)

        result = dest_conn.run(f"ls -tr {path}{directoriesEnergy[i]}/*.csv", hide=True)
        csv_files = result.stdout.strip().split("\n")
        for csv_file in csv_files:
            file_content = dest_conn.run(f'cat "{csv_file}"', hide=True).stdout

            #absolute_energy_consumption
            match = re.search(r'(\d+),\d+,Joules,power/energy-pkg/', file_content)
            absolute_energy_consumption.append(float(match.group(1))) if match else absolute_energy_consumption.append(0)

    #relative values
    relative_duration_time = [x / absolute_duration_time[8] for x in absolute_duration_time]
    relative_energy_consumption = [x / absolute_energy_consumption[8] for x in absolute_energy_consumption]
    relative_ipc = [absolute_ipc[8] / x for x in absolute_ipc]
    
    #edp
    absolute_edp = [(e * d) for e, d in zip(absolute_energy_consumption, absolute_duration_time)]
    max_edp = absolute_energy_consumption[8] * absolute_duration_time[8]
    relative_edp = [ (e * d) / max_edp for e, d in zip(absolute_energy_consumption, absolute_duration_time) ]

    #adding data to dataset
    absolute_duration_time_dataset.append(absolute_duration_time)
    relative_duration_time_dataset.append(relative_duration_time)
    absolute_energy_consumption_dataset.append(absolute_energy_consumption)
    relative_energy_consumption_dataset.append(relative_energy_consumption)
    absolute_edp_dataset.append(absolute_edp)
    relative_edp_dataset.append(relative_edp)
    relative_ipc_dataset.append(relative_ipc)


dataset = [absolute_duration_time_dataset, relative_duration_time_dataset,
        absolute_energy_consumption_dataset, relative_energy_consumption_dataset,
        absolute_edp_dataset, relative_edp_dataset, relative_ipc_dataset]
#plot.plotCoreAllocation(dataset, "Step-48")
