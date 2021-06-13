from make_toml import make_toml
from plot import *
from cell import *
import toml
import sys

def run():
    # Read toml config
    toml_str = open(sys.argv[2], "r").read()
    config = toml.loads(toml_str)


    # Check that files are found
    files = check_files(config["files"])


    # Define plot specifications
    plot = Plot(numfiles=len(files), **config["settings"])


    # Run the data reading + plot generation
    for f in files:
        Cell(f[0], f[1], plot=plot, start_cut = 40)


    plot.draw()

if __name__ == "__main__":
    if sys.argv[1] == "init":
        make_toml("./")
    elif sys.argv[1] == "run":
        run()

    
