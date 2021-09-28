# -*- coding: utf-8 -*-

"""This file is ran when user calls ecdh"""
from log import LOG
LOG.set_level("DEBUG")
from readers import check_files

from make_toml import make_toml
from plot import *
from cell import *
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

    toml_str = open(path, "r").read()
    config = toml.loads(toml_str)
    settings = config["settings"]

    # Check that files are found
    files = check_files(config["files"])
    LOG.success("Running ECDH: Found {} datafiles!".format(len(files)))

    # Define plot specifications
    plot = Plot(numfiles=len(files), **settings)


    # Run the data reading + plot generation
    cells = []
    for f in files:
        cell = Cell(f[0], f[1], plot=plot)
        cell.get_data()
        #cell.edit_CV()
        #cell.treat_data(settings)
        cell.plot()
        #cells.append(cell)



    plot.draw()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        run()
    elif sys.argv[1] == "init":
        make_toml("./")
    elif sys.argv[1] == "run":
        run()

    
