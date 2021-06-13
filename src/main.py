from plot import *
from cell import *
import toml
import sys

# Read toml config
toml_str = open(sys.argv[1], "r").read()
config = toml.loads(toml_str)


# Check that files are found
files = check_files(config["files"])


# Define plot specifications
plot = Plot(numfiles=len(files), **config["settings"])


# Run the data reading + plot generation
for f in files:
    Cell(f[0], f[1], plot=plot, start_cut = 0)


plot.draw()
