# Dependencies: Pandas, openpyxl
# CLI input 1 is data filepath
import os
import sys
from datetime import date
from math import ceil, sqrt

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import openpyxl as px
from matplotlib.lines import Line2D

from readers import csv_neware_to_vq, xlsx_neware_to_vq
from utils import simplify


class Cell:
    def __init__(self, filename, am_mass, plot = None, start_cut = 0):
        self.fn = filename
        self.am_mass = am_mass
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
            self.charges, self.discharges = csv_neware_to_vq(self.fn) #but this gives nested list with V/q data for each cycle.

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


class Plot:
    def __init__(self, 
                    percentage = False,
                    qcplot = True, 
                    vqplot = True,
                    suptitle = 'Capacity retention',
                    ylabel = 'Specific capacity [mAh/g]',
                    xlabel = "Cycles",
                    numfiles = 1):
        self.percentage = percentage
        self.qcplot = qcplot
        self.vqplot = vqplot
        self.taken_subplots = 0
        
        # Finding number of subplots
        if qcplot == True and vqplot == False:
            self.subplots = 1
        elif qcplot == True and vqplot == True:
            self.subplots = 1 + numfiles
        elif qcplot == False and vqplot == True:
            self.subplots = numfiles

        
        # List of available colors
        self.colors =  ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan' ]

        # Initiate figure and axes
        if self.subplots > 2: # Then two columns, or more.
            rows = int(sqrt(self.subplots))
            cols = ceil(self.subplots/rows)
            self.fig, self.axes = plt.subplots(nrows = rows, ncols = cols)
            self.axes = self.axes.reshape(-1)
        else:
            self.fig, self.axes = plt.subplots(nrows = self.subplots)
        self.fig.suptitle(str(date.today()))
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
            #ylim = (2.9,5.2),
            #xlim = (0, 150),
            #xticks = (np.arange(0, 150), step=20)),
            #yticks = (np.arange(3, 5, step=0.2)),
            )
            ax.tick_params(direction='in', top = 'true', right = 'true')

        # If cycle life is to be plotted: Make the first subplot this.
        if qcplot == True:
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

    def give_subplot(self):
        ax = self.axes[self.taken_subplots]
        self.taken_subplots += 1 #Increment the subplots availability and give it to whomever.
        return ax


    def draw(self, save =False, show = True):
        
        if self.qcplot == True:
            # Get labels and handles for legend generation and eventual savefile
            handles, labels = self.axes[0].get_legend_handles_labels()
            handles.append(Line2D([0], [0], marker='o', color='black', alpha = 0.2, label = 'Charge capacity', linestyle=''))
            self.axes[0].legend(handles=handles)
            # Title also has to be adjusted
        
        # Makes more space.
        #self.fig.subplots_adjust(hspace=0.4, wspace=0.4)

        # Save if True, If out path specified, save there.
        if save == True:
            savename = "CapRet"
            for label in labels:
                savename += "_" + label
            plt.savefig(savename)
        elif type(save) == str:
            plt.savefig(save)

        if show == True:
            plt.show()

            
    def get_color(self):
        give_color = self.colors[0]
        self.colors = self.colors[1:]
        return give_color

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


Files = [   ["4_LNMO_V2_E1_C4.csv", 0.01],
            ["./temp/Halvor_B_Mn15_15_3_1_O2_127.0.0.1_71_10_5_2818574827_20210222233438.xlsx", 0.00537],
            ["./temp/AMR_LNMO_B1_M2_C3_127.0.0.1_71_10_6_2818574808.xlsx", 0.00559]]


plot = Plot(percentage = True, qcplot = True, vqplot = True , numfiles=len(Files)) # qc = charge over cycle life, vq = voltage over charge

for f in Files:
    Cell(f[0], f[1], plot=plot, start_cut = 0)

plot.draw()