# ecdh - ElectroChemical Data Handling

edch provides easy solutions for simple handling of electrochemical data. Most emphasis is so far put on how to display the data using matplotlib.


## Usage:

Run ```src/main.py``` with python3.

Command line arguments:

- **init** initializes a toml file with the name *ecdh.toml*. Any supported datafiles in the local directory will be added to it.
- **run config.toml** runs with the configuration set in config.toml

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

Custom Packages:
- Matplotlib
- Numpy
- toml


## Examples

I have three datafiles from different equipment, but since they are all in the same folder, I can initiate a config file with the *init* command, and run it afterwords with *run ecdh.toml*.

The terminal looks like:

```
$ python3 ../src/main.py init
[INFO] Wrote example configuration to 'ecdh.toml' with 3
       files found
$ python3 ../src/main.py run ecdh.toml 
[INFO] Reading file: 'Neware_commasep.csv'
[INFO] Reading file: 'Biologic-text.mpt'
[INFO] Active mass found in file to be: 1e-06g
[INFO] Datafile ended with a Discharge
[INFO] Reading file: 'batsmall_data.dat'
```

Which yields the following output:
![](example_multiplot.png)

If I now enter the *ecdh.toml* file and set *dqdvplot = true*, *qcplot = false* and remove the entry of the ugly files, The output is:

![](example_dqdv.png)

## TODO list

- Enable specific cycles on a per-file basis
- Add Withaker-despiker smoothing algorithm to dQ/dV data
- Make dQ/dV and V/Q plot in the same figure if both are to be plotted 
