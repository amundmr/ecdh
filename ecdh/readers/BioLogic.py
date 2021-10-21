"""Data-readers for BioLogic"""

from ecdh.log import LOG

import numpy as np
import pandas as pd


def mpt_biologic_to_vq_old(filepath):
    import numpy as np
    f = open(filepath, 'r') #open the filepath for the mpt file
    # now we skip all the data in the start and jump straight to the dense data
    headerlines = 0
    for line in f:
        if "Nb header lines :" in line:
            headerlines = int(line.split(':')[-1])
            break #breaks for loop when headerlines is found
    
    for line in f:
        if "Characteristic mass :" in line:
            active_mass = float(line.split(':')[-1][:-3].replace(',', '.'))/1000
            LOG.success("Active mass found in file to be: " + str(active_mass) + "g")
            break #breaks loop when active mass is found

    #Skip all headerlines
    for i in range(headerlines):
        f.readline()


    #Put all the data in one big list of lines
    data = f.readlines()

    #Spawning massive data arrays for Potential, Charge and Cycle num
    Ewe_arr = np.zeros(len(data))
    Q_chg_dischg_arr = np.zeros_like(Ewe_arr)
    Cycle_arr = np.zeros_like(Ewe_arr)
    ox_red = np.zeros_like(Ewe_arr)

    #Putting all data (potential, capacity, cyclenum) in arrays
    i=-1
    for line in data: #Looping over each line in the dense data
        
        i+=1
        line_lst = line.split() #Splitting the line to a list
        Cycle_arr[i] = int(float(line_lst[-2].replace(',', '.'))) #The integer of the last element on the line as cycle added to array of cycles
        Ewe_arr[i] = float(line_lst[11].replace(',', '.')) #line elem 11 added to Ewe arr as float
        Q_chg_dischg_arr[i] = float(line_lst[19].replace(',', '.')) / active_mass
        ox_red[i] = int(float(line_lst[1].replace(',', '.')))
        

    #Creating list with indexes of new cycle starts
    list_of_cycleindexes = [0]
    list_of_reversalindexes = []
    for i in range(len(Cycle_arr)-1):
        if Cycle_arr[i]+1 == Cycle_arr[i+1]: #Adding the index where a new cycle starts (stop discharge, start charge)
            list_of_cycleindexes.append(i+1)
        if ox_red[i] == ox_red[i+1]+1: #Adding the index where the charge stops and the discharge starts
            list_of_reversalindexes.append(i+1)

    charges = []
    discharges = []
    indx = list_of_cycleindexes
    [indx.append(i) for i in list_of_reversalindexes]
    indx.sort()

    for i in range(len(indx) - 1):
        if (i%2) == 0: #even index: charge cycle
            charges.append((Ewe_arr[indx[i]:indx[i+1]], Q_chg_dischg_arr[indx[i]:indx[i+1]])) #Inserting tuple of two arrays sliced to be one cycle of voltages and capacities.
        else: #then discharge
            discharges.append((Ewe_arr[indx[i]:indx[i+1]], Q_chg_dischg_arr[indx[i]:indx[i+1]]))
    return charges, discharges
    

def read_mpt(filepath):
    """
    Reads an mpt file to a pandas dataframe
    
    .MPT format:
        mode column: 1=Galvanostatic, 2=Linear Potential Sweep, 3=Rest

    """
    modes = {1: "Galvanostatic", 2 : "Linear Potential Sweep", 3 : "Rest"}

    #with open(filepath, 'r', encoding= "iso-8859-1") as f:  #open the filepath for the mpt file
    #    lines = f.readlines()
    with open(filepath, errors = 'ignore') as f:
        lines = f.readlines()

    # now we skip all the data in the start and jump straight to the dense data
    headerlines = 0
    for line in lines:
        if "Nb header lines :" in line:
            headerlines = int(line.split(':')[-1])
            break #breaks for loop when headerlines is found
    
    for line in lines:
        if "Characteristic mass :" in line:
            active_mass = float(line.split(':')[-1][:-3].replace(',', '.'))/1000
            LOG.debug("Active mass found in file to be: " + str(active_mass) + "g")
            break #breaks loop when active mass is found


    big_df = pd.read_csv(filepath, header=headerlines-1, sep="\t", encoding = "ISO-8859-1")
    LOG.debug("Dataframe column names: {}".format(big_df.columns))

    # Start filling dataframe
    df = big_df[['mode', 'time/s', 'Ewe/V', '<I>/mA', 'cycle number', 'ox/red']]

    # If it's galvanostatic we want the capacity
    mode = df['mode'].value_counts().idxmax() #Find mode with maximum occurences
    LOG.debug("Found cycling mode: {}".format(modes[mode]))
    if mode == 1:
        df = df.join(big_df['Capacity/mA.h'])
        df.rename(columns={'Capacity/mA.h': 'capacity/mAhg'}, inplace=True)


    # Replace , by . and make numeric from strings. Mode is already interpreted as int.
    df['time/s'] = pd.to_numeric(df['time/s'].str.replace(',','.'))
    df['Ewe/V'] = pd.to_numeric(df['Ewe/V'].str.replace(',','.'))
    df['<I>/mA'] = pd.to_numeric(df['<I>/mA'].str.replace(',','.'))
    df['cycle number'] = pd.to_numeric(df['cycle number'].str.replace(',','.')).astype('int32')
    df.rename(columns={'ox/red': 'charge'}, inplace=True)
    df['charge'].replace({1: True, 0: False}, inplace = True)

    #Adding attributes must be the last thing to do since it will not be copied when doing operations on the dataframe
    df.experiment_mode = mode
    
    
    return df
    

def custom_EC_export(filepath):
    import numpy as np
    with open(filepath, 'r') as f: #open the filepath for the mpt file
        f.readline()
        lines = f.readlines()

    #Ox/red-col = 1
    #Ewe-col = 4
    #Cap-col = 5
    #Cyc-col = 0
    #Cur-col = 3
    #time-col = 2
    charges = []
    discharges = []
    newox = False
    oldox = eval(lines[0].split()[1])
    oldcap = 0
    t_prev = 0
    t_cycstart = 0
    tmp_cyc_E = []
    tmp_cyc_C = []
    Cap_cum = []
    for line in lines:
        if oldox == eval(line.split()[1]):
            tmp_cyc_E.append(eval(line.split()[4]))
            tmp_cyc_C.append(eval(line.split()[5]))
            
            #Manual capacity calculation
            I_cur = eval(line.split()[3])
            t_cur = eval(line.split()[2])/3600 - t_cycstart
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
            tmp_cyc_E.append(eval(line.split()[4]))
            tmp_cyc_C.append(eval(line.split()[5]))

            t_cycstart = eval(line.split()[2])/3600 # Resetting time of start of cycle
            #Manual capacity calculation
            I_cur = eval(line.split()[3])
            t_cur = eval(line.split()[2])/3600 - t_cycstart
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
