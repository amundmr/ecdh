from plotter import *

# Define input files
Files = [   ["4_LNMO_V2_E1_C4.csv", 0.01],
            ["./temp/Halvor_B_Mn15_15_3_1_O2_127.0.0.1_71_10_5_2818574827_20210222233438.xlsx", 0.00537],
            ["./temp/AMR_LNMO_B1_M2_C3_127.0.0.1_71_10_6_2818574808.xlsx", 0.00559]]


# Define plot specifications
plot = Plot(percentage = True, 
            qcplot = True, 
            vqplot = True , 
            numfiles=len(Files))
"""
# Plot class specifications:
percentage = <bool>     // Only used when qc-plot = True and changes scale from specific capacity to percent of first cycle
qcplot = <bool>         // Displays capacity over cycle life plot
vqplot = <bool>         // Displays voltage versus capacity for all cycles
suptitle = <string>     // Changes the top title to whatever you put it to
ylabel = <string>       // Changes y-scale label on the vq plots
xlabel = <string>       // Changes x-scale label on the vq plots
numfiles = <int>        // Amount of files which is passed in the file list
"""

# Run the data reading + plot generation
for f in Files:
    Cell(f[0], f[1], plot=plot, start_cut = 0)

"""
# Cell class specifications
1st argument = <string> // Path of file to be plotted
2nd argument = <float>  // Active mass of whatever the data is made on
plot = <plot> object    // Describes which plot object to use. Normally this is the one specified above
start_cut = <int>       // Cuts specified number of cycles off the start of the data
"""


plot.draw()
