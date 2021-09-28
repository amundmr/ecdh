import os as os
import matplotlib.pyplot as plt

from __main__ import LOG

from pandas.core.frame import DataFrame

import readers
import utils


"""
# Cell class specifications
1st argument = <string> // Path of file to be plotted
2nd argument = <string> // Active mass of whatever the data is made on
plot = <plot> object    // Describes which plot object to use. Normally this is the one specified above
start_cut = <int>       // Cuts specified number of cycles off the start of the data
"""



class Cell:
    def __init__(self, filename, am_mass, plot = None,):
        self.fn = filename
        self.am_mass = float(am_mass)
        self.color = plot.get_color()
        self.name = os.path.basename(filename)
        self.plotobj = plot
        self.axes = []
        self.mode_dict = {'0': 'Unspecified', '1': 'Galvanostatic', '2': "CyclicVoltammetry", '3': "Rest"}


    def get_data(self):
        # Read input file
        self.df = readers.read(self.fn)
        LOG.debug("Data has been read successfully")

    def edit_CV(self):
        """Takes self.df and returns self.CVdata in the format:
        self.CVdata = [cycle1, cycle2, cycle3, ... , cycleN]
        cyclex = (chg, dchg)
        chg = np.array([[v1, v2, v3, ..., vn],[i1, i2, i3, ..., in]])
        So it is an array of the voltages and corresponding currents for a charge and discharge cycle in a cycle tuple in a list of cycles. 
        """
        if self.df.experiment_mode != 2: #If the data isnt gathered in a cyclic voltammetry experiment, then this doesn't work!
            LOG.warning("File '{}' is not a CV file! It is a {} file.".format(self.fn, self.mode_dict[str(self.df.experiment_mode)]))
        else:
            print(self.df.groupby('cycle number'))


    def get_chgs_dchgs(self):

        charges = []
        discharges = []
        newox = False
        oldox = eval(lines[headerlines].split()[1])
        oldcap = 0
        t_prev = 0
        t_cycstart = 0
        tmp_cyc_E = []
        tmp_cyc_C = []
        Cap_cum = []
        for line in lines[headerlines:]:
            if oldox == eval(line.split()[1]):
                tmp_cyc_E.append(eval(line.split()[9]))
                tmp_cyc_C.append(eval(line.split()[17]))
                
                #Manual capacity calculation
                I_cur = eval(line.split()[10])
                t_cur = eval(line.split()[7])/3600 - t_cycstart
                timedelta = t_cur - t_prev
                Cap_cum.append(abs(oldcap + I_cur * timedelta))
                t_prev = t_cur
                oldcap += I_cur * timedelta

            else:
                #print("End-Halfcycle-triggered")
                if oldox == 1: #Charge cycle
                    charges.append((np.array(tmp_cyc_E), np.array(Cap_cum))) # Making the lists into arrays and putting them in a tuple as a charge cycle
                elif oldox == 0: #Discharge cycle
                    discharges.append((np.array(tmp_cyc_E), np.array(Cap_cum)))
                
                # Resetting the temporary lists
                tmp_cyc_E = []
                tmp_cyc_C = []
                Cap_cum = []
                t_prev = 0
                oldcap = 0
                # Setting the new ox status
                oldox = eval(line.split()[1])
                # Must remember to add this line's values!
                tmp_cyc_E.append(eval(line.split()[9]))
                tmp_cyc_C.append(eval(line.split()[17]))

                t_cycstart = eval(line.split()[7])/3600 # Resetting time of start of cycle
                #Manual capacity calculation
                I_cur = eval(line.split()[10])
                t_cur = eval(line.split()[7])/3600 - t_cycstart
                timedelta = t_cur - t_prev
                Cap_cum.append(oldcap + I_cur * timedelta)
                t_prev = t_cur
                oldcap += I_cur * timedelta

        # Adding the last data to arrays if the file ends
        if oldox == 1: #Charge cycle
            LOG.debug("Datafile ended with a Charge")
            charges.append((np.array(tmp_cyc_E), np.array(Cap_cum))) # Making the lists into arrays and putting them in a tuple as a charge cycle
        elif oldox == 0: #Discharge cycle
            LOG.debug("Datafile ended with a Discharge")
            discharges.append((np.array(tmp_cyc_E), np.array(Cap_cum)))

        return charges, discharges  

    def treat_data(self, config):
        LOG.debug("Treating data")
        if config["start_cut"]:
            start_cut = int(config["start_cut"])
            # Trimming cycles
            if start_cut > len(self.discharges) or self.start_cut > len(self.charges):
                LOG.warning(f"Start cut is set to {self.start_cut} but the number of discharges is only {len(self.discharges)}. Cuts will not be made.")
            else:
                LOG.debug("Cutting off start cycles")
                self.discharges = self.discharges[self.start_cut:]
                self.charges = self.charges[self.start_cut:]

    def plot(self):
        if self.df.experiment_mode == 2:
            self.plotobj.plot_CV(self)
        # Plot it
        """if self.plotobj.qcplot == True:
            self.plot_cyclelife(self.plotobj)
        if self.plotobj.vqplot == True:
            self.plot_cycles(self.plotobj)
        if self.plotobj.dqdvplot == True:
            self.plot_dqdv(self.plplotobjot)"""
        #if self.plotobj.dqdvplot == True and self.plotobj.vqplot == True:
        #    self.plot_cycles_dqdv(self.plotobj)


    def plot_cyclelife(self, plot):
        chgs, dischgs = self.simplify(self.charges, self.discharges) # Simplifies nested list to just capacities (and removes unwanted start cycles)
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
        chg = self.charges
        dchg = self.discharges
        #Define lengths for use with colors
        Nc = len(chg)
        Nd = len(dchg)

        ax = plot.give_subplot() #Recieve correct subplot axis object from plot
        self.axes.append(ax)

        if type(plot.specific_cycles) != bool:
            for i, (charge_cycle, discharge_cycle) in enumerate(zip(chg, dchg)):
                if i in plot.specific_cycles: 
                    ax.plot(charge_cycle[1]/self.am_mass, charge_cycle[0],  c = plot.cycle_color(i))
                    ax.plot(discharge_cycle[1]/self.am_mass, discharge_cycle[0], label = make_label(i), c = plot.cycle_color(i))
                ax.legend()
        else:
            for i, (charge_cycle, discharge_cycle) in enumerate(zip(chg, dchg)):
                ax.plot(charge_cycle[1]/self.am_mass, charge_cycle[0],  c = cmap(i/Nc))
                ax.plot(discharge_cycle[1]/self.am_mass, discharge_cycle[0],  c = cmap(i/Nd))

            # Adding colorbar to plot
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=Nd))
            sm._A = []
            plot.fig.colorbar(sm, ax=ax, label = "Cycle number")

        # Fixing title
        title = "VQ: " + os.path.basename(self.fn)
        ax.set_title(title)

        

    def plot_dqdv(self, plot):
        cmap = plot.colormap(self.color) #create colormap for fade from basic color
        # Slice to remove initial cycles Division by am mass to get specific capacity
        chg, dchg = make_dQdV(self.charges[self.start_cut:], self.discharges[self.start_cut:])
        #Define lengths for use with colors
        Nc = len(chg)
        Nd = len(dchg)

        ax = plot.give_subplot() #Recieve correct subplot axis object from plot
        self.axes.append(ax)

        if type(plot.specific_cycles) != bool:
            for i, (charge_cycle, discharge_cycle) in enumerate(zip(chg, dchg)):
                if i in plot.specific_cycles:
                    ax.plot(charge_cycle[1], charge_cycle[0],  c = plot.cycle_color(i))
                    ax.plot(discharge_cycle[1], discharge_cycle[0],  label = make_label(i), c = plot.cycle_color(i))
                ax.legend()
        else:
            for i, (charge_cycle, discharge_cycle) in enumerate(zip(chg, dchg)):
                ax.plot(charge_cycle[1], charge_cycle[0],  c = cmap(i/Nc))
                ax.plot(discharge_cycle[1], discharge_cycle[0],  c = cmap(i/Nd))
            # Adding colorbar to plot
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=Nd))
            sm._A = []
            plot.fig.colorbar(sm, ax=ax, label = "Cycle number")

        # Fixing title
        title =  "dQ/dV: " + os.path.basename(self.fn)
        ax.set_title(title)
        ax.set(ylabel = "Potential [V]", xlabel = "dQ/dV [mAh/Vg]")

    def simplify(self, chg, dchg):
        # Takes two lists of complete cycle data and returns max capacity for each cycle.
        # chg = [cycle1, cycle2, cycle3 , ... , cycleN]
        # cycle1 = [[v1, v2, v3, ..., vn],[q1, q2, q3, ..., qn]]
        # This func basically just pulls qn from every cycle and creates a new array with it.
        import numpy as np

        charges = np.zeros(len(chg))
        discharges = np.zeros(len(dchg))
        for i, cycle in enumerate(chg):
            try:
                charges[i] = cycle[1][-1]
            except:
                charges[i] = 0
        for i, cycle in enumerate(dchg):
            try:
                discharges[i] = cycle[1][-1]
            except:
                discharges[i] = 0
        return charges, discharges