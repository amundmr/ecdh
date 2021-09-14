import os
from __main__ import LOG

def make_toml(folder):
    files = []
    extlist = ["mpt", "csv", "dat", "xlsx"]


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
percentage = false              # Wether or not to use percentage in capacity vs cycles plot
qcplot = true                   # Wether or not to plot capacity vs cycles
vqplot = true                   # Wether or not to plot voltage versus capacity plot (cycling curves)
dqdvplot = false                # Wether or not to plot dQ/dV plots from the GCPL data
specific_cycles = false         # Will make global limit of cycles, can be range or list of cycles
suptitle = 'Capacity retention' # Title of plot
ylabel = 'Specific capacity [mAh/g]'
xlabel = 'Cycles'
"""

    with open("ecdh.toml", "w") as f:
        f.write(toml_str)
        info("Wrote example configuration to 'ecdh.toml' with %.0f files found"%len(files))