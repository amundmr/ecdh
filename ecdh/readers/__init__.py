# -*- coding: utf-8 -*-

"""
Author: Amund M. Raniseth
Readers take care of getting the data from the input file. 

Input: the filepath of any compatible datafile

Returns: pandas dataframe with 

    Columns:
    ['mode', 'charge', 'time/s','Ewe/V', '<I>/mA', 'cycle number', 'capacity/mAhg']

    Other variables:
    df.experiment_mode
    df.name
    where experiment mode is the most present mode in the 'mode' column and the modes are:
    1=Galvanostatic, 2=Linear Potential Sweep, 3=Rest
"""

from ecdh.log import LOG

from ecdh import utils

import os
import pandas as pd

def read(filepath):
    """
    Takes a filepath, finds out what file type it is, and reads it into two list of lists, fix this! maybe Cell object? or pd array?"""
    # Check input file and create proper data thereafter
    fn, ext = os.path.splitext(filepath)
    LOG.debug(f"Reading file: '{filepath}'")
    if ext == ".xlsx":
        from ecdh.readers import Neware as NA
        df = NA.read_xlsx(filepath)
    elif ext == ".csv":
        from ecdh.readers import Neware as NA
        df = NA.read_csv(filepath) #but this gives nested list with V/q data for each cycle.
    elif ext == ".mpt":
        from ecdh.readers import BioLogic as BL
        df = BL.read_mpt(filepath)
    elif ext == ".txt":
        from ecdh.readers import BatSmall as BS
        df = BS.read_txt(filepath)
    else:
        LOG.error(f"File format not supported: {ext}")
        LOG.error("Exiting..")
        exit()

    return df


def check_files(list):
    # Checks that files exist and then returns the ones that does.
    return_list = []
    for file in list:
        filename = file[0]
        if os.path.isfile(filename):
            return_list.append(file)
        else:
            LOG.error("File not found: '" + str(filename) + "' Please check that the correct path is typed in your input toml file. Skipping this file.")
    return return_list

