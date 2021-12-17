# -*- coding: utf-8 -*-
import os
from ecdh.log import LOG

def make_toml(folder):
    files = []
    extlist = ["mpt", "csv", "txt", "xlsx", "ecdh"]


    #Loop over all elements in current directory
    for entry in os.listdir(folder):
        # If it is a file and has the correct extension
        if os.path.isfile(entry) and entry.split(".")[-1] in extlist:
            # Add it to filelist
            files.append(entry)

    toml_str = """# Data path and active mass (set to 1 if data is normalized with regards to active mass)
files = [\n"""
    if len(files)>0:
        for file in files:
            toml_str += '\t["' + file + '","1.0"],\n'
    else:
        LOG.warning("Could not find any files in the current folder!")
        toml_str += '\t[" ","1.0"],\n'

    toml_str += """]

[settings]
qcplot = true                   # Wether or not to plot capacity vs cycles
percentage = false              # Wether or not to use percentage in capacity vs cycles plot
rawplot = true                  # Wether or not to plot Potential and Current vs time
rawplot_capacity = false        # Wether or not to use cumulative capacity on x-axis
vcplot = false                  # Wether or not to plot voltage curves (either CV og GC depending on data)
dqdvplot = false                # Wether or not to plot dQ/dV plots from the GCPL data
specific_cycles = false         # Will make global limit of cycles, can be range or list of cycles
suptitle = 'Capacity retention' # Title of plot
ylabel = 'Specific capacity [mAh/g]'
xlabel = 'Cycles'
all_in_one = true

[datatreatment]
reduce_data = false             # Reduces large files by changing potential resolution to 10mV and time resolution to 10s (new file is saved at same location as input file)
dt = 10                         # Maximum voltage which goes by unrecorded
dV = 0.01                       # Maximum time which goes by unrecorded
smooth_data = false             # removes outliers, new file saved at same location as input file
"""

    with open("ecdh.toml", "w") as f:
        f.write(toml_str)
        LOG.info("Wrote example configuration to 'ecdh.toml' with %.0f files found"%len(files))