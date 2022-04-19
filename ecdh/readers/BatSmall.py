# -*- coding: utf-8 -*-
"""Data-readers for Neware"""

from ecdh.log import LOG
def dat_batsmall_to_vq(filename): #NOT USING PD DATAFRAME YET
    import numpy as np
    data = []
    decode_errors = 0
    decode_error_str = ""
    with open(filename, "r") as f:
        # Skip all non-data lines
        while True:
            line = f.readline()
            if '"V";I:"A";C:"Ah/kg";7' in line:
                break
        # Adding the rest of the readable file to a data array
        while True:
            try:
                line = f.readline()
                if line == '':
                    break
                else:
                    data.append(line)
            except UnicodeDecodeError as e:
                decode_errors += 1
                decode_error_str = e
                continue
        
        if decode_errors > 0:
            LOG.warning("Found %i Unicode Decode errors, thus %i lines of data has been missed. Consider getting a safer method of acquiring data. \nComplete error message: " %(decode_errors, decode_errors) + str(decode_error_str))


    charges = []
    discharges = []
    charge = True
    voltages = []
    capacities = []

    for line in data[:-1]:

        try:
            v = float(eval(line.split(";")[1]))
            q = abs(float(eval(line.split(";")[3])))
            voltages.append(v)
            capacities.append(q)
        except:
            if '"V";I:"A";C:"Ah/kg"' in line and charge == True:
                #LOG.debug("Charge end at: V: %.5f, Q: %.5f" %(v,q))
                charges.append((np.array(voltages), np.array(capacities)))
                charge = False
                voltages = []
                capacities = []
            elif '"V";I:"A";C:"Ah/kg"' in line and charge == False:
                #LOG.debug("Discharge end at: V: %.5f, Q: %.5f" %(v,q))
                discharges.append((np.array(voltages), np.array(capacities)))
                charge = True
                voltages = []
                capacities = []

    return charges, discharges

def read_txt(filepath):
    """
    Author: Amund M. Raniseth
    Reads a txt file to a pandas dataframe

    .txt format:
        line 1: user comment
        header: includes columns TT, U, I, Z1 ++ , corresponding to time, potential, current and cycle number

    Important: In the datafile, in the first line (which is the user description) you must use the keyword CV or GC to tell what type of data it is."""
    import pandas as pd
    import numpy as np
    import os
    import gc

    # Open file
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find out what type of experiment this is
    expmode = 0
    for line in lines:
        if "CV" in line or "Cyclic Voltammetry" in line or "cyclic voltammetry" in line:
            expmode = 2
            break
        elif "GC" in line or "Galvanostatic" in line or "galvanostatic" in line:
            expmode = 1
            break
        else:
            LOG.warning("Cannot find out which type of experiment the file {} is! Please specify either CV or GC in the comment on the top of the file.".format(os.path.basename(filepath)))
            break

    # Find out how many headerlines this file have
    headerlines = 0
    for i,line in enumerate(lines):
        if 'TT' in line and 'U ' in line and 'I ' in line:
            headerlines = i
            break

    # Read all data to a pandas dataframe
    try:
        big_df = pd.read_csv(filepath, header = headerlines-1, sep = "\t")
    except UnicodeDecodeError as e:
        LOG.debug(f"Ran in to UnicodeDecodError in readers/BatSmall.py, reading with ANSI encoding. Error: {e}")
        big_df = pd.read_csv(filepath, header = headerlines-1, sep = "\t", encoding = 'ANSI')
    
    #Extract useful columns, change the name of the columns, make all numbers numbers.
    def _which_cap_col(big_df):
        for col in big_df.columns:
            if 'C [mAh/kg]' in col:
                return 'C [mAh/kg]'
            elif 'C [Ah/kg]' in col:
                return 'C [Ah/kg]'

    def _which_time_col(big_df):
        for col in big_df.columns:
            if 'TT [h]' in col:
                return 'TT [h]'
            elif 'TT [s]' in col:
                return 'TT [s]'

    df = big_df[[_which_time_col(big_df), 'U [V]', 'I [mA]', 'Z1 []', _which_cap_col(big_df)]]
    del big_df #deletes the dataframe
    gc.collect() #Clean unused memory (which is the dataframe above)
    if 'C [Ah/kg]' in df.columns:
        df['C [Ah/kg]'] = df['C [Ah/kg]'].apply(lambda x: abs(x*1000)) #Convert from Ah/kg to mAh/kg
    df.columns = ['time/s','Ewe/V', '<I>/mA', 'cycle number', 'capacity/mAhg'] #Renaming the columns. columns={'TT [h]': 'time/s', 'U [V]': 'Ewe/V', 'I [mA]': '<I>/mA', 'Z1 []':'cycle number', 'C [mAh/kg]':'capacity/mAhg'}, inplace=True)
    df = df.astype({"time/s": float, "Ewe/V": float, "<I>/mA": float, "capacity/mAhg": float, "cycle number": int})
    if 'TT [h]' in df.columns:
        df['time/s'] = df['time/s'].apply(lambda x: x*3600) #Converting from h to s
    df['capacity/mAhg'] = df['capacity/mAhg'].apply(lambda x: abs(x/1000)) #Convert from mAh/kg to mAh/g
    df['mode'] = expmode
    df['charge'] = True
    df.experiment_mode = expmode
    df.name = os.path.basename(filepath)
    
    check_df(df)

    df = clean_df(df)

    return df

def check_df(df):
    """Check if the dataframe has:
    - cycle number (sometimes the Z1 counter fucks up and just says 0)
    - If it is GC data: then calculate capacity
    
    If anything is wrong, it tries to fix it"""


    if df.experiment_mode == 1: #Then its GC
        if df['cycle number'].eq(0).all() or df['cycle number'].max() < 20: #If all cycle numbers are 0, then maybe Z1 counter was not iterated properly.
            LOG.info("We only found one cycle in '{}', and suspect this to be false. Checking now if there should be more cycles.".format(df.name))

            #We fix this by counting our own cycles.
            #Keeping track of signs of current (positive or negative) and cycle number
            prev_sign = True
            sign = True 
            cycle_number = 1
            new_cycle_indexes = []

            for i,current in df['<I>/mA'].items():

                if current > 0:
                    sign = True
                    df['charge'].at[i-1] = True
                elif current < 0:
                    sign = False
                    df['charge'].at[i-1] = False
                

                if prev_sign is False and sign is True:
                    #Changing from a discharge to a charge means new cycle
                    prev_sign = True
                    cycle_number += 1
                    #df['cycle number'].at[i-1] = cycle_number
                    new_cycle_indexes.append(i-1)
                    
                elif prev_sign is True and sign is False:
                    #Changing from a charge to a discharge
                    prev_sign = False
                    new_cycle_indexes.append(i-1)

                # In place editing of cycle number
                df['cycle number'].at[i] = cycle_number

            #Remove rows where a new experiment start (BatSmall has fucked datalogging here, where the current and voltage is the same as the prev step, but the capacity restarts)
            df.drop(new_cycle_indexes, axis = 0, inplace = True)

            if cycle_number > 1:
                LOG.info("Found {} cycles in {}".format(cycle_number, df.name))
            else:
                LOG.info("There seems to only be one cycle. Sorry for wasting your time.")

        else: #charge bool then isnt fixed
            for i,current in df['<I>/mA'].items():

                if current > 0:
                    sign = True
                    df['charge'].at[i-1] = True
                elif current < 0:
                    sign = False
                    df['charge'].at[i-1] = False


def clean_df(df):
    """
    Author: Amund M. Raniseth
    19.04.2022
    Features:
    - Removes time-shifts occuring in the data
    """

    df.reset_index(inplace = True) # The loop below relies on perfect indexing
    df["dt"] = df["time/s"].diff() # Make a column with timedeltas

    largedtindexes = df[df["dt"] > 60].index.values #Retrieve all indexes where timedelta is larger than 60

    # Loop to correct time shift. Reversed in order to properly shift all remaining time
    for indx in largedtindexes[::-1]:
        # Find time before shift and time after shift
        starttime = df.at[indx-1, "time/s"]
        endtime = df.at[indx, "time/s"]
        # shift time from this index and out
        df.loc[indx : , "time/s"] -= (endtime-starttime)



    return df
                
