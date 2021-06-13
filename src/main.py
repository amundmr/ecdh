from plot import *
from cell import *
import toml
import sys

toml_str = open(sys.argv[1], "r").read()
config = toml.loads(toml_str)

print(config["settings"])


# Define plot specifications
plot = Plot(numfiles=len(config["files"]), **config["settings"])


# Run the data reading + plot generation
for f in config["files"]:
    Cell(f[0], f[1], plot=plot, start_cut = 0)




plot.draw()
