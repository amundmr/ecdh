# -*- coding: utf-8 -*-
"""Data-readers for BioLogic"""

from ecdh.log import LOG

import numpy as np
import pandas as pd
import gc

def read_mpt(filepath):
    """
    Author: Amund M. Raniseth
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
    
    for i,line in enumerate(lines):
        #You wont find Characteristic mass outside of headerlines.
        if headerlines > 0:
            if i > headerlines:
                break
        
        if "Characteristic mass :" in line:
            active_mass = float(line.split(':')[-1][:-3].replace(',', '.'))/1000
            LOG.debug("Active mass found in file to be: " + str(active_mass) + "g")
            break #breaks loop when active mass is found

    # pandas.read_csv command automatically skips white lines, meaning that we need to subtract this from the amout of headerlines for the function to work.
    whitelines = 0
    for i, line in enumerate(lines):
        #we dont care about outside of headerlines.
        if headerlines > 0:
            if i > headerlines:
                break
        if line == "\n":
            whitelines += 1

    #Remove lines object
    del lines
    gc.collect()


    big_df = pd.read_csv(filepath, header=headerlines-whitelines-1, sep = "\t", encoding = "ISO-8859-1")
    LOG.debug("Dataframe column names: {}".format(big_df.columns))

    # Start filling dataframe
    if 'I/mA' in big_df.columns:
        current_header = 'I/mA'
    elif '<I>/mA' in big_df.columns:
        current_header = '<I>/mA'
    df = big_df[['mode', 'time/s', 'Ewe/V', current_header, 'cycle number', 'ox/red']]
    # Change headers of df to be correct
    df.rename(columns={current_header: '<I>/mA'}, inplace=True)

    # If it's galvanostatic we want the capacity
    mode = df['mode'].value_counts() #Find occurences of modes
    mode = mode[mode.index != 3] #Remove the count of modes with rest (if there are large rests, there might be more rest datapoints than GC/CV steps)
    mode = mode.idxmax()    # Picking out the mode with the maximum occurences
    LOG.debug("Found cycling mode: {}".format(modes[mode]))

    if mode == 1:
        df = df.join(big_df['Capacity/mA.h'])
        df.rename(columns={'Capacity/mA.h': 'capacity/mAhg'}, inplace=True)
        if df.dtypes['capacity/mAhg'] == str: #the str.replace only works and is only needed if it is a string
            df['capacity/mAhg'] = pd.to_numeric(df['capacity/mAhg'].str.replace(',','.'))
    del big_df #deletes the dataframe
    gc.collect() #Clean unused memory (which is the dataframe above)
    # Replace , by . and make numeric from strings. Mode is already interpreted as int.
    for col in df.columns:
        if df.dtypes[col] == str: #the str.replace only works and is only needed if it is a string
            df[col] = pd.to_numeric(df[col].str.replace(',','.'))
    #df['time/s'] = pd.to_numeric(df['time/s'].str.replace(',','.'))
    #df['Ewe/V'] = pd.to_numeric(df['Ewe/V'].str.replace(',','.'))
    #df['<I>/mA'] = pd.to_numeric(df['<I>/mA'].str.replace(',','.'))
    #df['cycle number'] = pd.to_numeric(df['cycle number'].str.replace(',','.')).astype('int32')
    df.rename(columns={'ox/red': 'charge'}, inplace=True)
    df['charge'].replace({1: True, 0: False}, inplace = True)

    #Adding attributes must be the last thing to do since it will not be copied when doing operations on the dataframe
    df.experiment_mode = mode
    
    return df
    

