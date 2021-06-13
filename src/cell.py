import os as os
import matplotlib.pyplot as plt

from readers import csv_neware_to_vq, dat_batsmall_to_vq, xlsx_neware_to_vq
from utils import simplify


"""
# Cell class specifications
1st argument = <string> // Path of file to be plotted
2nd argument = <string> // Active mass of whatever the data is made on
plot = <plot> object    // Describes which plot object to use. Normally this is the one specified above
start_cut = <int>       // Cuts specified number of cycles off the start of the data
"""

class Cell:
    def __init__(self, filename, am_mass, plot = None, start_cut = 0):
        self.fn = filename
        self.am_mass = float(am_mass)
        self.color = plot.get_color()
        self.name = os.path.basename(filename).split("_127.0.0")[0]
        self.start_cut = start_cut
        self.plot = plot

        self.auto_run()


    def auto_run(self):
        # Check input file and create proper data thereafter
        fn, ext = os.path.splitext(self.fn)
        if ext == ".xlsx":
            self.charges, self.discharges = xlsx_neware_to_vq(self.fn)
        elif ext == ".csv":
            self.charges, self.discharges = csv_neware_to_vq(self.fn)
        elif ext == ".dat":
            self.charges, self.discharges = dat_batsmall_to_vq(self.fn)

        # Plot it
        if self.plot.qcplot == True:
            self.plot_cyclelife(self.plot)
        if self.plot.vqplot == True:
            self.plot_cycles(self.plot)


    def plot_cyclelife(self, plot):
        chgs, dischgs = simplify(self.charges[self.start_cut:], self.discharges[self.start_cut:]) # Simplifies nested list to just capacities (and removes unwanted start cycles)

        norm_fact = dischgs[0]
        if plot.percentage == True: #Normalize capacities on the first cycle.
            dischgs /= norm_fact
            chgs /= norm_fact
        else: # If not precentage, then it is specific
            dischgs /= self.am_mass
            chgs /= self.am_mass

        plot.axes[0].scatter(range(len(dischgs)), dischgs, label=self.name, color = self.color)
        plot.axes[0].scatter(range(len(chgs)), chgs, color = self.color, alpha = 0.2 )

    def plot_cycles(self, plot):
        cmap = plot.colormap(self.color) #create colormap for fade from basic color
        # Slice to remove initial cycles Division by am mass to get specific capacity
        chg = self.charges[self.start_cut:]
        dchg = self.discharges[self.start_cut:]
        #Define lengths for use with colors
        Nc = len(chg)
        Nd = len(dchg)

        ax = plot.give_subplot() #Recieve correct subplot axis object from plot

        for i, (charge_cycle, discharge_cycle) in enumerate(zip(chg, dchg)):
            ax.plot(charge_cycle[1]/self.am_mass, charge_cycle[0],  c = cmap(i/Nc))
            ax.plot(discharge_cycle[1]/self.am_mass, discharge_cycle[0],  c = cmap(i/Nd))


        # Fixing title
        title = os.path.basename(self.fn)
        ax.set_title(title)

        # Adding colorbar to plot
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=Nd))
        sm._A = []
        plot.fig.colorbar(sm, ax=ax, label = "Cycle number")
