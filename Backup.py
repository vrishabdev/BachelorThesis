import numpy as np
import PlotData as plot

#dataset = np.load(f"./Data/Step-37/datasetPowerCapping.npy", allow_pickle=True)
#plot.plotPowerCapping(dataset, "Step-37")

dataset = np.load(f"./Data/Step-6/datasetCPUFrequency.npy", allow_pickle=True)
plot.plotCPUFrequency(dataset, "Step-6")