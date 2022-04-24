# -*- coding: utf-8 -*-
import os
import toml
from ecdh.log import LOG

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
                "suptitle":             (False, "Title of plot                      "),
                "ylabel":               (False, "Y Abcissa label                    "),
                "xlabel":               (False, "X Abcissa label                    "),
                "legend_location":      ('best', "Options: 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'"),
                "all_in_one":           (False, "[NOT WORKING]Puts all different datafiles in same plot"),
                "savefig":              (False, "Save figure, false, true or path to save to."),
                },
            "datatreatment": {
                "reduce_data":          (False, "Reduces large files by changing potential resolution to 10mV and time resolution to 10s (new file is saved at same location as input file)"),
                "dt":                   (10, "Maximum time which goes by unrecorded"),
                "dv":                   (0.01, "Maximum voltage change which goes by unrecorded"),
                "smooth_data":          (False, "removes outliers, new file saved at same location as input file"),
                "print_capacities":      (False, "Will print the capacity of the plotted cycles within a potential range, can be false or list of pairwise ranges, eg: [3.5, 4.5, 4.5, 5.0] does the analysis in the ranges 3.5V-4.5V and 4.5V-5.0V"),
                }
            }


def make_toml(folder):
    files = []
    extlist = ["mpt", "csv", "txt", "xlsx", "ecdh"]


    #Loop over all elements in current directory
    for entry in os.listdir(folder):
        # If it is a file and has the correct extension
        if os.path.isfile(entry) and entry.split(".")[-1] in extlist:
            # Add it to filelist
            files.append(entry)

    toml_str = """# "Data path", "active mass" and "nickname" (set active mass to 1 if data is normalized with regards to active mass)
files = [\n"""
    if len(files)>0:
        for file in files:
            toml_str += '\t["' + file + '","1.0"],\n'
    else:
        LOG.warning("Could not find any files in the current folder!")
        toml_str += '\t[" ","1.0"],\n'

    toml_str += "]\n\n"
    toml_str += gen_string(cfg_dict)

    with open("ecdh.toml", "w") as f:
        f.write(toml_str)
        LOG.info("Wrote example configuration to 'ecdh.toml' with %.0f files found"%len(files))

def gen_string(cfg_dict):
    masterstr = ""
    for key, item in cfg_dict.items():
        masterstr += "[" + key + "]\n"
        lines = []
        for subkey, subitem in item.items():
            if type(subitem[0]) is bool or type(subitem[0]) is float or type(subitem[0]) is int:
                kwarg_default_value = str(subitem[0]).lower()
            elif type(subitem[0]) is str:
                kwarg_default_value = "'" + str(subitem[0]) + "'"
            else:
                LOG.debug("Keyword in cfg_dict conf.py found to be neither str nor bool nor float nor int. This needs special handling.")
                kwarg_default_value = "false"

            left_align = subkey + " = " + kwarg_default_value
            center_align = "# " + subitem[1]
            lines.append(f"{left_align : <30} {center_align : ^30}")

        for line in lines:
            masterstr += line + "\n"
        masterstr += "\n"
    return masterstr

def read_config(path):
    try:
        toml_str = open(path, "r").read()
    except Exception as e:
        LOG.error(f"Couldn't read config file: {e}")
        import sys
        sys.exit()
        
    # Check toml string
    check_config(toml_str)
    # Fill toml config
    config = toml.loads(toml_str)
    config = fill_config(config)
    return config

def check_config(string):
    return 0

def fill_config(dictionary):

    # Hardcoding this to save time
    for key, value in cfg_dict["settings"].items():
        if key not in dictionary["settings"]:
                dictionary["settings"][key] = value[0]

    for key, value in cfg_dict["datatreatment"].items():
        if key not in dictionary["datatreatment"]:
                dictionary["datatreatment"][key] = value[0]

    return dictionary
