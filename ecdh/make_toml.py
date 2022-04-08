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
qcplot = false                   # Wether or not to plot capacity vs cycles
coulombicefficiency = true      # True will plot CE on twin x axis with cycle life in qcplot
percentage = false              # Wether or not to use percentage in capacity vs cycles plot
rawplot = true                  # Wether or not to plot Potential and Current vs time
rawplot_capacity = false        # Wether or not to use cumulative capacity on x-axis
vcplot = false                  # Wether or not to plot voltage curves (either CV og GC depending on data)
hysteresisview = false          # True will remove the absolute and reset of capacity for better hysteresis viewing
dqdvplot = false                # Wether or not to plot dQ/dV plots from the GCPL data
specific_cycles = false         # Will make global limit of cycles, can be range or list of cycles
cycle_range = false             # Cycle range you want to plot in list format like [10, 40]
suptitle = 'Capacity retention' # Title of plot
ylabel = 'Specific capacity [mAh/g]'
xlabel = 'Cycles'
legend_location = 'best'        # Options: 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'
all_in_one = false
savefig = false                 # Save figure, false, true or path to save to.

[datatreatment]
reduce_data = false             # Reduces large files by changing potential resolution to 10mV and time resolution to 10s (new file is saved at same location as input file)
dt = 10                         # Maximum time which goes by unrecorded
dV = 0.01                       # Maximum voltage which goes by unrecorded
smooth_data = false             # removes outliers, new file saved at same location as input file
print_capacities = false        # Will print the capacity of the plotted cycles within a potential range, can be false or list of tuples, eg: [(3.8, 4.5), (4.5, 5.0)]
"""

    with open("ecdh.toml", "w") as f:
        f.write(toml_str)
        LOG.info("Wrote example configuration to 'ecdh.toml' with %.0f files found"%len(files))

cfg_dict = {"settings": {
                "qcplot":               (False,"Wether or not to plot capacity vs cycles") ,
                "coulombicefficiency":  (True, "True will plot CE on twin x axis with cycle life in qcplot"),
                "percentage":           (False, "Wether or not to use percentage in capacity vs cycles plot"),
                "rawplot":              (True, "Wether or not to plot Potential and Current vs time"),
                "rawplot_capacity":     (False, "Wether or not to use cumulative capacity on x-axis"),
                "vcplot":               (False, "Wether or not to plot voltage curves (either CV og GC depending on data)"),
                "hysteresisview":       (False, "True will remove the absolute and reset of capacity for better hysteresis viewing"),
                "dqdvplot":             (False, "Wether or not to plot dQ/dV plots from the GCPL data"),
                "specific_cycles":      (False, "Will make global limit of cycles, can be range or list of cycles"),
                "cycle_range":          (False, "Cycle range you want to plot in list format like [10, 40]"),
                "suptitle":             (False, "Title of plot"),
                "ylabel":               (False, "Y Abcissa label"),
                "xlabel":               (False, "X Abcissa label"),
                "legend_location":      ('best', "Options: 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'"),
                "all_in_one":           (False, "[NOT WORKING]Puts all different datafiles in same plot"),
                "savefig":              (False, "Save figure, false, true or path to save to."),
                },
            "datatreatment": {
                "reduce_data":          (False, "Reduces large files by changing potential resolution to 10mV and time resolution to 10s (new file is saved at same location as input file)"),
                "dt":                   (10, "Maximum time which goes by unrecorded"),
                "dv":                   (0.01, "Maximum voltage change which goes by unrecorded"),
                "smooth_data":          (False, "removes outliers, new file saved at same location as input file"),
                "print_capacities":      (False, "Will print the capacity of the plotted cycles within a potential range, can be false or list of tuples, eg: [(3.8, 4.5), (4.5, 5.0)]"),
                }
            }