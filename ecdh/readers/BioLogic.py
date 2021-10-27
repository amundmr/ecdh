"""Data-readers for BioLogic"""

from ecdh.log import LOG

import numpy as np
import pandas as pd
import gc

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
    mode = df['mode'].value_counts() #Find occurences of modes
    mode = mode[mode.index != 3] #Remove the count of modes with rest (if there are large rests, there might be more rest datapoints than GC/CV steps)
    mode = mode.idxmax()    # Picking out the mode with the maximum occurences
    LOG.debug("Found cycling mode: {}".format(modes[mode]))

    if mode == 1:
        df = df.join(big_df['Capacity/mA.h'])
        df.rename(columns={'Capacity/mA.h': 'capacity/mAhg'}, inplace=True)
        df['capacity/mAhg'] = pd.to_numeric(df['capacity/mAhg'].str.replace(',','.'))
    del big_df #deletes the dataframe
    gc.collect() #Clean unused memory (which is the dataframe above)
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
    

