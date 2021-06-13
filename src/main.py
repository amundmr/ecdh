from plot import *
from cell import *


# Define input files
Files = [   ["4_LNMO_V2_E1_C4.csv", 0.01],
            ["./temp/Halvor_B_Mn15_15_3_1_O2_127.0.0.1_71_10_5_2818574827_20210222233438.xlsx", 0.00537],
            ["./temp/AMR_LNMO_B1_M2_C3_127.0.0.1_71_10_6_2818574808.xlsx", 0.00559]]


# Define plot specifications
plot = Plot(percentage = True, 
            qcplot = True, 
            vqplot = True , 
            numfiles=len(Files))


# Run the data reading + plot generation
for f in Files:
    Cell(f[0], f[1], plot=plot, start_cut = 0)




plot.draw()
