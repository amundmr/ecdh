# -*- coding: utf-8 -*-
import os as os
import matplotlib.pyplot as plt

from ecdh.log import LOG

from pandas.core.frame import DataFrame

import ecdh.readers as readers
import ecdh.utils as utils


"""
# Cell class specifications ***OUTDATED***
1st argument = <string> // Path of file to be plotted
2nd argument = <string> // Active mass of whatever the data is made on
plot = <plot> object    // Describes which plot object to use. Normally this is the one specified above
start_cut = <int>       // Cuts specified number of cycles off the start of the data
"""



class Cell:
    def __init__(self, filename, am_mass, nickname, plot = None, specific_cycles = None):
        self.fn = filename
        try:
            self.am_mass = float(am_mass)
        except:
            self.am_mass = None
        if plot:
            self.color = plot.get_color()
        else:
            self.color = "black"

        if nickname:
            self.name = nickname
        else:
            self.name = os.path.basename(filename)
        self.plotobj = plot
        self.axes = []
        self.mode_dict = {'0': 'Unspecified', '1': 'Galvanostatic', '2': "CyclicVoltammetry", '3': "Rest"}
        self.specific_cycles = specific_cycles
        self.GCdata = None
        self.CVdata = None
        self.CVdata_capacity = None


    def get_data(self):
        # Read input file
        self.df = readers.read(self.fn)
        LOG.debug("Data has been read successfully")


    def edit_CV_capacity(self):
        import numpy as np
        LOG.error("Cell.py/edit_CV_capacity has not been made! Creating data with only zeros.")
        self.CVdata_capacity = [(np.array([[0], [0]]), np.array([[0], [0]]))]


    def edit_CV(self):
        import numpy as np
        """Takes self.df and returns self.CVdata in the format:
        self.CVdata = [cycle1, cycle2, cycle3, ... , cycleN]
        cyclex = (chg, dchg)
        chg = np.array([[v1, v2, v3, ..., vn],[i1, i2, i3, ..., in]])
        So it is an array of the voltages and corresponding currents for a charge and discharge cycle in a cycle tuple in a list of cycles. 
        """
        if self.df.experiment_mode != 2: #If the data gathered isn't a cyclic voltammetry experiment, then this doesn't work!
            LOG.warning("File '{}' is not a CV file! It is a {} file.".format(self.fn, self.mode_dict[str(self.df.experiment_mode)]))
        else:
            self.CVdata = []

            #Remove all datapoints where mode != 2, we dont care about other data than CV here.
            index_names = self.df[self.df['mode'] != 2].index
            rawCVdata = self.df.drop(index_names)

            for cycle, subframe in rawCVdata.groupby('cycle number'):

                #Split into charge and discharge data
                chgdat = subframe[subframe['charge'] == True]
                dchgdat = subframe[subframe['charge'] == False]

                cycle = (np.array([chgdat['Ewe/V'], chgdat['<I>/mA']]), np.array([dchgdat['Ewe/V'], dchgdat['<I>/mA']]))
                self.CVdata.append(cycle)


    def edit_GC(self):
        import numpy as np
        import pandas as pd
        """Takes self.df and returns self.GCdata in the format:
        self.GCdata = [cycle1, cycle2, cycle3, ... , cycleN]
        cyclex = (chg, dchg)
        chg = np.array([[q1, q2, q3, ..., qn],[v1, v2, v3, ..., vn]]) where q is capacity"""
        if self.df.experiment_mode != 1: #If the data gathered isn't a galvanostatic experiment, then this doesn't work!
            LOG.warning("File '{}' is not a GC file! It is a {} file.".format(self.fn, self.mode_dict[str(self.df.experiment_mode)]))
        else:
            self.GCdata = []

            #Remove all datapoints where mode != 1, we dont care about other data than GC here.
            index_names = self.df[self.df['mode'] != 1].index
            rawGCdata = self.df.drop(index_names)
            
            for cycle, subframe in rawGCdata.groupby('cycle number'):

                #Split into charge and discharge data
                chgdat = subframe[subframe['charge'] == True].copy(deep=True)
                dchgdat = subframe[subframe['charge'] == False].copy(deep=True)
                #print(subframe.head)



                if self.am_mass or 'capacity/mAhg' not in self.df.columns:
                    if not self.am_mass:
                        self.am_mass = 1
                    #The inserted Active material mass might differ from the one the instrument software calculated. Thus we make our own capacity calculations.
                    from scipy import integrate
                    #Integrate current over time, returns mAh, divide by active mass to get gravimetric
                    #Placed inside try/except because sometimes the lenght of chgdat["<I>/mA"] or dch is 0 (when the cycle has started but the second redox mode hasnt started), then cumtrapz will fail.
                    try:
                        chgdat.loc[:,'capacity/mAhg'] = integrate.cumtrapz(abs(chgdat["<I>/mA"]), chgdat["time/s"]/3600, initial = 0) / self.am_mass


                    except Exception as e:
                        LOG.debug(f"something went wrong with the scipy.integrate.cumtrapz in cell.py under edit_GC: {e}")
                        if not chgdat.empty:
                            chgdat.loc[:,'capacity/mAhg'] = 0
                        else:
                            chgdat['capacity/mAhg'] = []


                    try:
                        dchgdat.loc[:,'capacity/mAhg'] = integrate.cumtrapz(abs(dchgdat["<I>/mA"]), dchgdat["time/s"]/3600, initial = 0)/ self.am_mass
                    except:
                        if not dchgdat.empty:
                            dchgdat.loc[:,'capacity/mAhg'] = 0
                        else:
                            dchgdat['capacity/mAhg'] = []

                cycle = (np.array([chgdat['capacity/mAhg'], chgdat['Ewe/V']]), np.array([dchgdat['capacity/mAhg'], dchgdat['Ewe/V']]))
                self.GCdata.append(cycle)

            if self.plotobj.hysteresisview:
                #Then it should be plottet hysteresis-style
                last_cycle_capacity = 0
                for cycle in self.GCdata:
                    #offsett all the capacity by the last cycles last capacity
                    #cycle[1][0] += last_cycle_capacity
                    #make the discharge capacity negative and offset it so it starts from the last charge capacity
                    cycle[1][0] *= -1
                    cycle[1][0] += cycle[0][0][-1]
                    #Update the variable so the next cycle is offset by the correct amount
                    try:
                        last_cycle_capacity = cycle[1][0][-1]
                    except Exception as e:
                        LOG.debug(f"cell.py edit_GC if hysteresisview: couldn't get the last capacity element of the discharge: {e}")
                    
            

    def edit_cyclelife(self):
        import numpy as np
        import pandas as pd
        #First make sure that we have either CV capacity data or galvanostatic
        if self.df.experiment_mode == 2:
            if not self.CVdata_capacity:
                LOG.error("in cell/edit_cyclelife, CVdata_capacity has not been made.")
                self.edit_CV_capacity() 

        elif self.df.experiment_mode == 1:
            #If the GC data doesn't exist, make it.
            if not self.GCdata:
                self.edit_GC()

            #Make temporary dataholders
            tmpdat = []
            #loop through data and gather capacities
            for i, cycle in enumerate(self.GCdata):
                chg, dchg = cycle
                try:
                    tmpdat.append([i, chg[0][-1], dchg[0][-1]])
                except:
                    try:
                        tmpdat.append([i, chg[0][-1],0 ])
                    except:
                        try:
                            tmpdat.append([i, 0, dchg[0][-1]])
                        except:
                            tmpdat.append([i, 0, 0])

            self.cyclelifedata = pd.DataFrame(tmpdat, columns = ["cycle", "charge capacity/mAh", "discharge capacity/mAh"])

            self.cyclelifedata["coulombic efficiency"] = self.cyclelifedata["discharge capacity/mAh"] / self.cyclelifedata["charge capacity/mAh"] * 100


    def edit_cumulative_capacity(self):
        """This function is used when you want the cumulative capacity for plotting potential and current versus capacity in a raw data plot"""
        LOG.debug("Calculating the cumulative capcity..")
        from scipy import integrate
        cumulative_capacity = integrate.cumtrapz(abs(self.df["<I>/mA"]), self.df["time/s"]/3600, initial = 0)
        self.df["CumulativeCapacity/mAh/g"] = cumulative_capacity/self.am_mass
        

    def edic_dQdV(self):
        import numpy as np
        import pandas as pd
        """Takes self.df and returns self.dQdVdata in the format:
        self.dQdVdata = [cycle1, cycle2, cycle3, ... , cycleN]
        cyclex = (chg, dchg)
        chg = np.array([[v1, v2, v3, ..., vn],[dqdv1, dqdv2, dqdv3, ..., dqdvn]]) where dqdv is dQ/dV"""
        if self.df.experiment_mode != 1: #If the data gathered isn't a galvanostatic experiment, then this doesn't work!
            LOG.warning("File '{}' is not a GC file! It is a {} file.".format(self.fn, self.mode_dict[str(self.df.experiment_mode)]))
        else:
            self.dQdVdata = []
            
            #Remove all datapoints where mode != 1, we dont care about other data than GC here.
            index_names = self.df[self.df['mode'] != 1].index
            rawGCdata = self.df.drop(index_names)
            
            for cycle, subframe in rawGCdata.groupby('cycle number'):

                #Split into charge and discharge data
                chgdat = subframe[subframe['charge'] == True].copy(deep=True)
                dchgdat = subframe[subframe['charge'] == False].copy(deep=True)

                #The inserted Active material mass might differ from the one the software calculated. Thus we make our own capacity calculations.
                if self.am_mass:
                    from scipy import integrate
                    #Integrate current over time, returns mAh, divide by active mass to get gravimetric.

                    try:
                        chgdat.loc[:,'capacity/mAhg'] = integrate.cumtrapz(abs(chgdat["<I>/mA"]), chgdat["time/s"]/3600, initial = 0)/ self.am_mass

                    except Exception as e:
                        LOG.debug(f"something went wrong with the scipy.integrate.cumtrapz in cell.py under edit_GC: {e}")
                        if not chgdat.empty:
                            chgdat.loc[:,'capacity/mAhg'] = 0
                        else:
                            chgdat['capacity/mAhg'] = []

                    try:
                        dchgdat.loc[:,'capacity/mAhg'] = integrate.cumtrapz(abs(dchgdat["<I>/mA"]), dchgdat["time/s"]/3600, initial = 0)/ self.am_mass
                    except Exception as e:
                        LOG.debug(f"something went wrong with the scipy.integrate.cumtrapz in cell.py under edit_GC: {e}")
                        if not dchgdat.empty:
                            dchgdat.loc[:,'capacity/mAhg'] = 0
                        else:
                            dchgdat['capacity/mAhg'] = []
                
                def binit(x,y, Nbins = 120):
                    # extract 120 elements evenly spaced in the data
                    Nbins = 120
                    binsize = int(len(x)/Nbins)
                    if binsize == 0: # modulo by zero not allowed so filtering that here
                        return [0], [0]

                    i = 0
                    xar = []
                    yar = []
                    for i,(x,y) in enumerate(zip(x,y)):
                        if i%binsize == 0:
                            xar.append(x)
                            yar.append(y)
                    return xar, yar
               
                def moving_average(x,y, w=9):
                    if len(x) < w + 1 or len(y) < w + 1:
                        return [0], [0]

                    from scipy.signal import savgol_filter
                    # Savitzky-Golay filter
                    #y = savgol_filter(y, w, 3)
                    #x = savgol_filter(x, w, 3)
                    #Simple Moving average
                    x = np.convolve(x, np.ones(w), 'valid') / w
                    y = np.convolve(y, np.ones(w), 'valid') / w
                    return x, y

                def get_dqdv(x,y):
                    x,y = binit(x,y)
                    x,y = moving_average(x,y)

                    if len(x)< 2 or len(y) < 2:
                        return [0],[0]

                    dqdv = np.log(np.diff(x)/np.diff(y))
                    v = y[:-1]
                    return dqdv, v

                chg_dqdv, chg_v = get_dqdv(chgdat['capacity/mAhg'], chgdat['Ewe/V'])
                dchg_dqdv, dchg_v = get_dqdv(dchgdat['capacity/mAhg'], dchgdat['Ewe/V'])

                cycle = (np.array([chg_v, chg_dqdv]), np.array([dchg_v, dchg_dqdv]))
                self.dQdVdata.append(cycle)


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


    def reduce_data(self, datatreatment):
        """
        Takes the data and deletes points not matching the requirement.
        Useful if you measured with too high sampling rate and have gigantic datafiles
        Example: you sampled for every 1mV change, and every second, then with dV = 0.010 and dt = 10, all points that has less than a difference of 10mV AND less than 10s will be deleted.
        """
        LOG.debug("cell.reduce_data() is running, reducing file: {}".format(self.name))
        LOG.info("Reducing file: {}. Follow loading bar below, this might take some time.".format(self.name))

        try:
            dt = int(datatreatment["dt"])
        except:
            dt = 10
        try:
            dV = float(datatreatment["dV"])
        except:
            dV = 0.01


        #dt = 10 #10 s
        #dV = 0.01 # 10mV
        dI = 0.01 #0.01 mA, 10uA
        LOG.debug(f"Reduction parameters: dt: {dt}, dV: {dV}, dI: {dI}.")
        #'time/s','Ewe/V', '<I>/mA'
        last_t = self.df['time/s'].iloc[0]
        last_V = self.df['Ewe/V'].iloc[0]
        kill_index = []

        max_i = len(self.df)
        loadbar = 10
        print("|----------|")
        print("|", end ="", flush=True)
        for i,row in self.df.iloc[1:].iterrows():

            curr_t = row.iloc[0]
            curr_V = row.iloc[1]

            if abs(last_t - curr_t) < dt and abs(last_V - curr_V) < dV:
                kill_index.append(i)
            else:
                last_t = curr_t
                last_V = curr_V
            
            if i == int(max_i/loadbar):
                print("-", end="", flush=True)
                loadbar -= 1
                if loadbar < 1:
                    loadbar += 1 #Wow this needs fixing
        print("|")

        filename, ext = os.path.splitext(self.fn)
        self.df.drop(kill_index, inplace=True)
        self.df.to_csv(path_or_buf=filename+"_reduced.ecdh")

            
    def smooth_data(self, datatreatment):
        """
        Takes the data and removes outliers
        Useful if you have a couple of short circuits now and then
        
        """
        LOG.info(f"Removing outliers on {self.name}.")
        import pandas as pd
        window = int(len(self.df) / 10000)
        smoothing_df = pd.DataFrame()
        smoothing_df['median']= self.df['Ewe/V'].rolling(window).median()
        smoothing_df['std'] = self.df['Ewe/V'].rolling(window).std()

        expmode = self.df.experiment_mode
        #filter setup
        self.df = self.df[(self.df['Ewe/V'] <= smoothing_df['median']+3*smoothing_df['std']) & (self.df['Ewe/V'] >= smoothing_df['median']-3*smoothing_df['std'])].ewm(alpha = 0.9).mean()
        self.df.experiment_mode = expmode


    def get_capacities(self, datatreatment):
        """
        Returns capacity in a potential interval for each cycle.
        Appends to filename "./capacities.txt"
        """
        if not len(datatreatment['print_capacities'])%2 == 0:
            LOG.critical("You wanted to get the potential-interval capacities, but you inserted an odd number of boundaries. You need two boundaries for each range, eg: [3.5, 4.4, 4.4, 5.0] will be two ranges from 3.5->4.4 and 4.4->5.0. The capacities will not be printed.")
        else:
            intervals = []
            for i,pot in enumerate(datatreatment['print_capacities']):
                if i%2!=0: #if the index number is odd, we are making a range of it
                    intervals.append((datatreatment['print_capacities'][i-1], pot))
            LOG.info("Found intervals for capacity print: {}".format(intervals))
                    
            if self.GCdata:
                data = self.GCdata
            elif self.CVdata:
                data = self.CVdata
            else:
                self.edit_GC()
            
            import numpy as np
            def _find_charge(chg, interval):
                start, stop = interval
                cap , pot = chg
                pot = np.asarray(pot)
                idxstart = (np.abs(pot - start)).argmin()
                idxstop = (np.abs(pot - stop)).argmin()
                capdiff = cap[idxstop] - cap[idxstart]

                return abs(capdiff)

            # Format list like: [chg, dchg], chg = [cap in interval 1, cap in interval 2, cap in interval n]
            caps = {self.name : {}}
            for interval in intervals:
                caps[self.name][str(interval)] = { "charge" : [],
                                        "discharge": []}

            if self.specific_cycles:
                for i, cycle in enumerate(data):
                    if i in self.specific_cycles:
                        chg, dchg = cycle
                        for interval in intervals:
                            caps[self.name][str(interval)]["charge"].append(_find_charge(chg, interval))
                            caps[self.name][str(interval)]["discharge"].append(_find_charge(dchg, interval))

            else:
                for i,cycle in enumerate(data):
                    chg, dchg = cycle
                    for interval in intervals:
                        caps[self.name][str(interval)]["charge"].append(_find_charge(chg, interval))
                        caps[self.name][str(interval)]["discharge"].append(_find_charge(dchg, interval))

            
            return caps



    def plot(self):
        if not self.plotobj:
            LOG.error("No plot object supplied to the cell, but cell.plot was still called! Exiting..")
            import sys
            sys.exit()

        if self.plotobj.vcplot:
            if self.df.experiment_mode == 2:
                self.edit_CV()
                self.plotobj.plot_CV(self)
            elif self.df.experiment_mode == 1:
                self.edit_GC()
                self.plotobj.plot_GC(self)

        if self.plotobj.qcplot:
            self.edit_cyclelife()
            self.plotobj.plot_cyclelife(self)

        if self.plotobj.rawplot:
            if self.plotobj.rawplot_capacity:
                self.edit_cumulative_capacity()

            self.plotobj.plot_raw(self)

        if self.plotobj.dqdvplot:
            self.edic_dQdV()
            self.plotobj.plot_dQdV(self)