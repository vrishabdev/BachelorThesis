import pandas as pd

policy = ["PCoreFirst", "ECoreFirst", "Balanced"]
power_cap = ["50Watt", "75Watt", "100Watt", "175Watt", "253Watt"]
num_cores = [2, 4, 8, 12, 16, 20, 24, 28, 32]

def createTable(absolute_duration_time_dataset, absolute_energy_consumption_dataset, fileName):
    for i in range(3):
        table = []
        reference_value_duration_time = absolute_duration_time_dataset[i, 4, 8]
        reference_value_energy_consumption = absolute_energy_consumption_dataset[i, 4, 8]
        for j in range(5):
            for k in range(9):
                duration_time = absolute_duration_time_dataset[i, j, k]
                overhead_D = ((duration_time / reference_value_duration_time) - 1) * 100
                overhead_D = round(overhead_D, 1)

                energy_consumption = absolute_energy_consumption_dataset[i, j, k]
                overhead_E = ((energy_consumption / reference_value_energy_consumption) - 1) * 100
                overhead_E = round(overhead_E, 1)

                table.append({'Configuration': f'{policy[i]} - {power_cap[j]} - {num_cores[k]}cores',
                              'duration_time': f'{duration_time}s',
                              'energy_consumption': f'{energy_consumption}Joules',
                              'relative EDP': f'{(duration_time * energy_consumption) / (reference_value_duration_time * reference_value_energy_consumption)}',
                              '%Overhead (duration_time)': f'{overhead_D}%',
                              f'%Overhead (energy_consumption)': f'{overhead_E}%'})
        
        #save configurations in a csv file
        table = pd.DataFrame(table)
        table.to_csv(f"./Plots/{fileName}/PowerCapping/{policy[i]}/{policy[i]}.csv", index=False)
        print(table)

def createTableFrequency(absolute_duration_time_dataset, absolute_energy_consumption_dataset, fileName, number_of_freq):
    for i in range(2):
        table = []
        for j in range(5):
            for k in range(number_of_freq):
                duration_time = absolute_duration_time_dataset[j, k]
                energy_consumption = absolute_energy_consumption_dataset[j, k]
                relative_edp = (duration_time * energy_consumption) / (absolute_duration_time_dataset[4, number_of_freq - 1] * absolute_energy_consumption_dataset[4, number_of_freq - 1])
                table.append({'duration_time': f'{duration_time}s',
                              'energy_consumption': f'{energy_consumption}Joules',
                              'relative EDP': f'{relative_edp}'})
        
        #save configurations in a csv file
        type = "PCoreScaling" if number_of_freq == 11 else "ECoreScaling"
        table = pd.DataFrame(table)
        table.to_csv(f"./Plots/{fileName}/CPUFrequency/{type}/{type}.csv", index=False)
        print(table)