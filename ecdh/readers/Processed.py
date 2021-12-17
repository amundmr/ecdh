# -*- coding: utf-8 -*-
"""Data-readers for Data already processed by ecdh"""
from ecdh.log import LOG

import pandas as pd

def read_ecdh(filepath):
    """
    Author: Amund M. Raniseth
    Reads an ecdh file to a pandas dataframe
    
    .ecdh format:
        mode column: 1=Galvanostatic, 2=Linear Potential Sweep, 3=Rest

    """
    modes = {1: "Galvanostatic", 2 : "Linear Potential Sweep", 3 : "Rest"}

    df = pd.read_csv(filepath)

    # If it's galvanostatic we want the capacity
    mode = df['mode'].value_counts() #Find occurences of modes
    mode = mode[mode.index != 3] #Remove the count of modes with rest (if there are large rests, there might be more rest datapoints than GC/CV steps)
    mode = mode.idxmax()    # Picking out the mode with the maximum occurences
    LOG.debug("Found cycling mode: {}".format(modes[mode]))

    #Adding attributes must be the last thing to do since it will not be copied when doing operations on the dataframe
    df.experiment_mode = mode

    return df