# -*- coding: utf-8 -*-
import os
import sys
from datetime import date
from math import ceil, sqrt
from ecdh.log import LOG

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D

import numpy as np


"""
# Plot class specifications:
percentage = <bool>     // Only used when qc-plot = True and changes scale from specific capacity to percent of first cycle
qcplot = <bool>         // Displays capacity over cycle life plot
vcplot = <bool>         // Displays voltage curves (either CV or GC)
suptitle = <string>     // Changes the top title to whatever you put it to
ylabel = <string>       // Changes y-scale label on the vq plots
xlabel = <string>       // Changes x-scale label on the vq plots
numfiles = <int>        // Amount of files which is passed in the file list
"""

class Plot:
    def __init__(self, numfiles = 1, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.taken_subplots = 0
        
        # Finding number of subplots
        if self.qcplot is True:
            self.subplots = 1
        else:
            self.subplots = 0

        if self.all_in_one:
            if self.vcplot:
                self.subplots+= 1
            if self.rawplot:
                self.subplots += 1
            if self.dqdvplot:
                self.subplots += 1
        else:
            if self.vcplot is True:
                self.subplots += numfiles
            
            if self.dqdvplot is True:
                self.subplots += numfiles
            
            if self.rawplot:
                self.subplots += numfiles

        
        # List of available colors
        
        
        if numfiles > 10:
            tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),  
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),  
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),  
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),  
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
            for i in range(len(tableau20)):  
                r, g, b = tableau20[i]  
                tableau20[i] = (r / 255., g / 255., b / 255.)
            self.colors = tableau20
            LOG.warning("You have chosen to plot more than 10 files, which will look messy, but you do you.")
        else:
            tableau10 = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
            self.colors = tableau10
        # Initiate figure and axes
        if self.subplots > 2: # Then two columns, or more.
            rows = int(sqrt(self.subplots))
            cols = ceil(self.subplots/rows)
            self.fig, self.axes = plt.subplots(nrows = rows, ncols = cols)
            self.axes = self.axes.reshape(-1)
        else:
            self.fig, self.axes = plt.subplots(nrows = self.subplots)
        self.fig.suptitle(str(date.today()))

        #Make sure self.axes is a list if it is only 1 element
        try:
            iter(self.axes)
        except:
            self.axes = [self.axes]
        
        for ax in self.axes:
            #ax.figure.set_size_inches(8.4, 4.8, forward = True)
            ax.set(
            title = 'Generic subplot title',
            ylabel = 'Potential [V]',
            xlabel = 'Specific Capacity [mAh/g]',
            #ylim = (2.5,5),
            #xlim = (0, 150),
            #xticks = (np.arange(0, 150), step=20)),
            #yticks = (np.arange(3, 5, step=0.2)),
            )
            ax.tick_params(direction='in', top = 'true', right = 'true')

        # If cycle life is to be plotted: Make the first subplot this.
        if self.qcplot == True:
            self.taken_subplots +=1
            # Dealing with percentage
            if self.percentage == True:
                ylabel = 'Capacity retention [%]'
                self.axes[0].yaxis.set_major_formatter(mtick.PercentFormatter(xmax = 1, decimals = 0))
            else:
                ylabel = 'Specific capacity [mAh/g]'
            
            self.axes[0].set(
                title = 'Cycle life',
                ylabel = ylabel,
                xlabel = 'Cycles'
            )

        if self.rawplot and self.all_in_one:
            self.axtwinx = None

    def give_subplot(self):
        ax = self.axes[self.taken_subplots]
        self.taken_subplots += 1 #Increment the subplots availability and give it to whomever.
        return ax


    def draw(self, save =False, show = True):
        LOG.debug("Running plot.py draw()")
        if self.qcplot == True:
            # Get labels and handles for legend generation and eventual savefile
            handles, labels = self.axes[0].get_legend_handles_labels()
            handles.append(Line2D([0], [0], marker='o', color='black', alpha = 0.2, label = 'Charge capacity', linestyle=''))
            if self.coulombicefficiency:
                handles.append(Line2D([0], [0], marker='+', color='black', alpha = 0.2, label = 'Coulombic Efficiency', linestyle=''))
            try:
                loc = self.legend_location
            except Exception as e:
                loc = 'best'
                LOG.debug(f"Plot.py draw(), error with legend_location setting: {e}")
            self.axes[0].legend(handles=handles, loc=loc)
            if type(self.specific_cycles) != bool:
                self.axes[0].scatter(self.specific_cycles, np.zeros(len(self.specific_cycles)), marker = "|")
            # Title also has to be adjusted
        
        #if self.rawplot == True:
        #self.fig.suptitle("Cyclic voltammetry")
        #for ax in self.axes:
        #    ax.set_title("")

        # Makes more space.
        #self.fig.subplots_adjust(hspace=0.4, wspace=0.4)

        
        if self.all_in_one is True:
            plt.legend()

        # Save if True, If out path specified, save there.
        if save == True:
            """ Fix this sometime
            handles, labels = self.axes[0].get_legend_handles_labels()
            savename = "CapRet"
            for label in labels:
                savename += "_" + label"""
            plt.savefig("ecdhfig.png", bbox_inches='tight')
        elif type(save) == str:
            plt.savefig(save, bbox_inches='tight')

        if show == True:
            #plt.legend(loc='lower left')
            plt.show()


    def get_color(self):
        give_color = self.colors[0]
        self.colors = self.colors[1:]
        return give_color
        

    def cycle_color(self, ncycle):
        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),  
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),  
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),  
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),  
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
        tableau10 = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
        colors = tableau20
        return colors[self.specific_cycles.index(ncycle)]

    def colormap(self, color):
        color_hsv = np.asarray(mcolors.rgb_to_hsv(mcolors.to_rgb(color)))
        color_start = color_hsv.copy()
        color_end = color_hsv.copy()

        color_start[2] = 0
        color_end[2] = 1

        color1 = np.asarray(mcolors.hsv_to_rgb(color_start))*255
        color2 = np.asarray(mcolors.hsv_to_rgb(color_end))*255
        

        n = 100 #Numer of steps for colors
        diff = (color1-color2)/n
        colors = np.zeros((n,3))
        for i in range(len(colors)):
            colors[i] = color1 - i*diff
        colors = colors/255
        self.cmap = mpl.colors.LinearSegmentedColormap.from_list('colormap', colors)
        return self.cmap

    def plot_cyclelife(self, cellobj):
        """Takes a cell object and plots it in a cyclelife plot with either specific capacity or percentage on the y axis versus cycle number on the x axis"""
        data = cellobj.cyclelifedata

        norm_fact = data["discharge capacity/mAh"].iloc[0]

        if self.percentage == True: #Normalize capacities on the first cycle.
            data["discharge capacity/mAh"] = data["discharge capacity/mAh"] / norm_fact
            data["charge capacity/mAh"] = data["charge capacity/mAh"] / norm_fact
        # If not precentage, then it is just the raw data which has already been handled in edit_GC


        ax = self.axes[0]   #Getting the right plot
        Nc = cellobj.cyclelifedata.count      #finding max number of cycles
        # Plot it
        if not cellobj.specific_cycles: #Not specific cycles? then plot all.
            ax.scatter(cellobj.cyclelifedata["cycle"]+1, cellobj.cyclelifedata["charge capacity/mAh"],color = cellobj.color, alpha = 0.2)
            ax.scatter(cellobj.cyclelifedata["cycle"]+1, cellobj.cyclelifedata["discharge capacity/mAh"],color = cellobj.color, label = cellobj.name)

        else: #There are specific cycles
            #LOG.error("Specific cycles hasnt been implemented in lifecycle plot")
            filtered_data = cellobj.cyclelifedata[cellobj.cyclelifedata['cycle'].isin(cellobj.specific_cycles)]
            ax.scatter(filtered_data["cycle"]+1, filtered_data["charge capacity/mAh"],color = cellobj.color, alpha = 0.2)
            ax.scatter(filtered_data["cycle"]+1, filtered_data["discharge capacity/mAh"],color = cellobj.color, label = cellobj.name)
            #colorlist = self.colors
            #for i,cycle in enumerate(cellobj.cyclelifedata[3]):
            #    if cycle not in cellobj.specific_cycles:


        if self.coulombicefficiency:
            ax2 = ax.twinx()
            ax2.set_ylabel("Coulombic Efficiency [%]")
            ax2.set_ylim(50, 105)
            if not cellobj.specific_cycles: #Not specific cycles? then plot all.
                ax2.scatter(cellobj.cyclelifedata["cycle"]+1, cellobj.cyclelifedata["coulombic efficiency"], color = cellobj.color, marker = "+")
            else:
                filtered_data = cellobj.cyclelifedata[cellobj.cyclelifedata['cycle'].isin(cellobj.specific_cycles)]
                ax2.scatter(filtered_data["cycle"]+1, filtered_data["coulombic efficiency"], color = cellobj.color, marker = "+")


    def plot_CV(self, cellobj):
        """Takes a cellobject and plots it in a CV plot (I/mA vs Ewe/V)"""
        LOG.debug("Running plot.py plot_CV")
        # Get subplot from main plotclass
        if self.all_in_one is False:
            ax = self.give_subplot()
            ax.set_title(f"{cellobj.name}")
        else:
            ax = self.axes[0] if self.qcplot is False else self.axes[1]
            ax.set_title("Cyclic Voltammograms")
            
        #Placing it in a plot with correct colors
        self.insert_cycle_data(cellobj, ax, cellobj.CVdata)


        ax.set_ylabel("Current [mA]")
        ax.set_xlabel("Potential [V]")



    def plot_GC(self, cellobj):
        """Takes a cell dataframe and plots it in a GC plot (Ewe/V vs Cap)"""
        LOG.debug("Running plot.py plot_GC")

        # Get subplot from main plotclass
        if self.all_in_one is False:
            ax = self.give_subplot()
            ax.set_title(f"{cellobj.name}")
        else:
            ax = self.axes[0] if self.qcplot is False else self.axes[1]
            ax.set_title("Galvanostatic Cycling")
            
        #Placing it in a plot with correct colors
        self.insert_cycle_data(cellobj, ax, cellobj.GCdata)

        
        ax.set_xlabel(r"Capacity [$\frac{mAh}{g}$]")
        ax.set_ylabel("Potential [V]")


    def insert_cycle_data(self, cellobj, ax, data):
        """
        Inserts the given data in the given axis with data from the cellobject
        Data must be on form 
        data = [cycle1, cycle2, cycle3, ... , cycleN]
        cyclex = (chg, dchg)
        chg = np.array([[x1, x2, x3, ..., xn],[y1, y2, y3, ..., yn]]) where x is usually either capacity or potential and y usually potential or current
        """
        # Generating colormap
        cmap = self.colormap(cellobj.color) #create colormap for fade from basic color
        #Define cycle amount for use with colors
        Nc = len(data)



        # Plot it
        ## count number of specific cycles
        if cellobj.specific_cycles:
            numcyc = len(cellobj.specific_cycles)
        else:
            numcyc = 0

        if numcyc > 5 or Nc > 5: #Use colorbar if more than 4 cycles and no specific cycles.
            if cellobj.specific_cycles:
                maxcyc = max(cellobj.specific_cycles)
                for i,cycle in enumerate(data):
                    if i in cellobj.specific_cycles:
                        chg, dchg = cycle
                        ax.plot(chg[0], chg[1], color = cmap(i/maxcyc))
                        ax.plot(dchg[0], dchg[1], color = cmap(i/maxcyc))
            else:
                for i,cycle in enumerate(data):
                    chg, dchg = cycle
                    ax.plot(chg[0], chg[1], color = cmap(i/Nc))
                    ax.plot(dchg[0], dchg[1], color = cmap(i/Nc))

            # Adding colorbar to plot
            if cellobj.specific_cycles:
                maxcyc = max(cellobj.specific_cycles)
            else:
                maxcyc = Nc
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=maxcyc))
            sm._A = []
            if self.all_in_one is True:
                self.fig.colorbar(sm, ax=ax, label = "Cycle number for {}".format(cellobj.name))
            else:
                self.fig.colorbar(sm, ax=ax, label = "Cycle number")

        else: #There are either specific cycles or <=5 cycles in the data

            colorlist = self.colors
            if cellobj.specific_cycles:
                for i,cycle in enumerate(data):
                    if i in cellobj.specific_cycles:
                        color = colorlist[0]
                        colorlist = colorlist[1:]

                        chg, dchg = cycle
                        if self.all_in_one is True:
                            ax.plot(chg[0], chg[1], color = color, label = f"{cellobj.name} Cycle {i}") #This is the charge cycle
                        else:
                            ax.plot(chg[0], chg[1], color = color, label = "Cycle {}".format(i)) #This is the charge cycle
                        ax.plot(dchg[0], dchg[1], color = color) #1 is discharge
            else:
                for i,cycle in enumerate(data):

                    color = colorlist[0]
                    colorlist = colorlist[1:]

                    chg, dchg = cycle
                    if self.all_in_one is True:
                        ax.plot(chg[0], chg[1], color = color, label = f"{cellobj.name} Cycle {i}") #This is the charge cycle
                    else:
                        ax.plot(chg[0], chg[1], color = color, label = "Cycle {}".format(i)) #This is the charge cycle
                    ax.plot(dchg[0], dchg[1], color = color) #1 is discharge


    def plot_dQdV(self, cellobj):
        """Takes a cell dataframe and plots it in a dQdV plot (dQdV/mAhVg vs Ewe/V)"""
        LOG.debug("Running plot.py plot_dQdV")

        # Get subplot from main plotclass
        if self.all_in_one is False:
            ax = self.give_subplot()
            ax.set_title("dQdV: {}".format(os.path.basename(cellobj.fn)))
        else:
            ax = self.axes[0] if self.qcplot is False else self.axes[1]
            ax.set_title("dQdV")
            
        #Placing it in a plot with correct colors
        self.insert_cycle_data(cellobj, ax, cellobj.dQdVdata)

        
        ax.set_ylabel(r"dQ/dV [$log\left(\frac{mAh}{Vg}\right)$ smoothed]")
        ax.set_xlabel("Potential [V]")


    def plot_raw(self,cellobj):
        """Takes a cellobject and plots it in a raw data plot (I/mA and Ewe/V vs time/s)"""
        LOG.debug("Running plot.py plot_raw")
        # Get subplot from main plotclass
        if self.all_in_one is False:
            ax = self.give_subplot()
            ax.set_title("raw data: {}".format(os.path.basename(cellobj.fn)))
            #Initiate twin ax
            ax2 = ax.twinx()
            #self.axes.append(ax2)
        else:
            if self.qcplot and self.rawplot:
                ax = self.axes[2]
            elif self.all_in_one and not self.qcplot:
                ax = self.axes[0]
            elif self.all_in_one and self.qcplot:
                ax = self.axes[1]
            elif self.qcplot or self.rawplot: 
                ax = self.axes[1]
            else:
                ax = self.axes[0]
            #Initiate twin axis, only if it doesnt exist aleady
            if not self.axtwinx:
                self.axtwinx = ax.twinx()
            ax2 = self.axtwinx

            ax.set_title(self.suptitle)
            

        #if specific cycles, then remove all other cycles
        if cellobj.specific_cycles:
            df = cellobj.df[cellobj.df['cycle number'].isin(cellobj.specific_cycles)]
        else:
            df = cellobj.df

        
        #Placing it in a plot
        if self.rawplot_capacity:
            x = df["CumulativeCapacity/mAh/g"]
            ax.set_xlabel(r"Cumulative Capacity [$\frac{mAh}{g}$]")
        else:
            x = df["time/s"]/3600

            ax.set_xlabel("Time [h]")

        ax.plot(x, df["Ewe/V"], color = cellobj.color, label = cellobj.name)
        ax2.plot(x, df["<I>/mA"], color = cellobj.color, linestyle = "dotted")


        ax.set_ylabel("Potential [V]")
        ax2.set_ylabel("Current [mA]")
        