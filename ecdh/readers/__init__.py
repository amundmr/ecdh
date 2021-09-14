from __main__ import LOG
import readers.BatSmall as BS
import readers.BioLogic as BL
import readers.Neware as NA

import utils
import os

def read(filepath):
    """
    Takes a filepath, finds out what file type it is, and reads it into two list of lists, fix this! maybe Cell object? or pd array?"""
    # Check input file and create proper data thereafter
    fn, ext = os.path.splitext(filepath)
    LOG.debug(f"Reading file: '{filepath}'")
    if ext == ".xlsx":
        charges, discharges = NA.read_xlsx(filepath)
    elif ext == ".csv":
        charges, discharges = NA.read_csv(filepath) #but this gives nested list with V/q data for each cycle.
    elif ext == ".mpt":
        charges, discharges = BL.mpt_biologic_to_vq(filepath)
    elif ext == ".customexport":
        charges, discharges = BL.custom_EC_export(filepath)
    elif ext == ".dat":
        charges, discharges = BS.dat_batsmall_to_vq(filepath)
    else:
        LOG.error(f"File format not supported: {ext}")
        LOG.error("Exiting..")
        exit()

    return charges, discharges


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