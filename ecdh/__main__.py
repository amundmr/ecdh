# -*- coding: utf-8 -*-

"""This file is ran when user calls ecdh"""

from ecdh.log import LOG
LOG.set_level("DEBUG")
from ecdh.readers import check_files

from ecdh.make_toml import make_toml
from ecdh.plot import *
from ecdh.cell import *

import toml
import sys

def run():

    if len(sys.argv) < 3: #Then no folder is specified, look for toml in local folder.
        if os.path.isfile("./ecdh.toml"):
            path = "./ecdh.toml"
        else:
            LOG.error("Could not find an ecdh.toml file in the current directory! \nOptions: \n1. Run ecdh with the argument 'run' followed by the path of your .toml file. \n2. Initiate toml file in this directory with the init argument.")
            sys.exit()
    elif os.path.isfile(sys.argv[2]):# File was inserted Read toml config
        path = sys.argv[2]
    else:
        LOG.error("Cannot find the .toml configuration file!")
        sys.exit()
    LOG.debug("Reading config file: '{}'".format(path))
    toml_str = open(path, "r").read()
    config = toml.loads(toml_str)
    settings = config["settings"]
    # Merge cycle range into specific cycles
    if settings['cycle_range']:
        try:
            cyclerange = np.linspace(settings['cycle_range'][0], settings['cycle_range'][1], settings['cycle_range'][1]-settings['cycle_range'][0] + 1).astype(int)
            if type(settings['specific_cycles']) is bool:
                settings['specific_cycles'] = cyclerange.tolist()
            else:
                settings['specific_cycles'] += cyclerange.tolist()
            LOG.error(f"Specific cycles: {settings['specific_cycles']}")
        except Exception as e:
            LOG.warning(f"Could not use the cycle range, Error: {e}")


    datatreatment = config["datatreatment"]

    # Check that files are found
    files = check_files(config["files"])
    LOG.success("Running ECDH: Found {} datafiles!".format(len(files)))

    # Define plot specifications
    plot = Plot(numfiles=len(files), **settings)


    # Run the data reading + plot generation
    cells = []
    for f in files:
        try:
            am_mass = f[1]
        except:
            am_mass = None
        try:
            nickname = f[2]
        except:
            nickname = None

        cell = Cell(f[0], am_mass, nickname,  plot=plot, specific_cycles = settings['specific_cycles'])
        cell.get_data()
        #cell.edit_GC()
        #cell.treat_data(settings)
        cell.plot()
        #cells.append(cell)
        
        if datatreatment['reduce_data']:
            cell.reduce_data(datatreatment)

        if datatreatment['smooth_data']:
            cell.smooth_data(datatreatment)
        
        if datatreatment['print_capacities']:

            if not os.path.isfile("capacity_intervals.json"):
                with open("capacity_intervals.json", "w") as f:
                    f.close()

            import json
 
            new_json = cell.get_capacities(datatreatment)

            with open("capacity_intervals.json",'r+') as file:
                # First we load existing data into a dict.
                try:
                    file_data = json.load(file)
                except:
                    file_data = []
                # Join new_data with file_data inside emp_details
                file_data.append(new_json)
                # Sets file's current position at offset.
                file.seek(0)
                # convert back to json.
                json.dump(file_data, file, indent = 4)
            
            
            
        


    if 'savefig' in settings:
        plot.draw(save = settings['savefig'])
    else:
        plot.draw()

def main():
    if len(sys.argv) < 2:
        run()
    elif sys.argv[1] == "init":
        make_toml("./")
    elif sys.argv[1] == "run":
        run()
    else:
        LOG.critical("Can't interpret CLI parameters.")

if __name__ == "__main__":
    main()

    
