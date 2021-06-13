# WARNING
*This sofware is not complete, and at the moment not functioning*

# ecdh - ElectroChemical Data Handling

edch provides easy solutions for simple handling of electrochemical data. Most emphasis is so far put on how to display the data using matplotlib.


## Usage:

Run ```src/main.py``` with python3.

Command line arguments:
**init** initializes a toml file with the name *ecdh.toml*. Any supported datafiles in the local directory will be added to it.
**run config.toml** runs with the configuration set in config.toml

Example use:
```
python3 src/main.py init
python3 src/main.py run ecdh.toml 
```


## Features:

- Galvanostatic Cycling
    - Plot Charge/Discharge curves over cycle life
        - Range, specific or all cycles can be plotted in addition to trimming of the first *x* cycles.
    - Plot Capacity retention over cycle life
    - Plot dQ/dV: Smoothing coming
    - Plot data from any number of input files
- Cyclic Voltammetry
    - Still in the works...


## Supported Input filetypes:

- Neware backup files (.xlsx)
- Neware export as general report (.csv)
- Biologic (.mpt)
- Batsmall (.dat)


## Dependencies
Standard Packages:
- os
- sys
- datetime
- math
- textwrap

Custom Packages:
- Matplotlib
- Numpy
- toml
