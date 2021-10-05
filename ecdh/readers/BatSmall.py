"""Data-readers for Neware"""

from ecdh.log import LOG
def dat_batsmall_to_vq(filename):
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
        #print(line.split(";"))
        try:
            v = float(eval(line.split(";")[1]))
            q = abs(float(eval(line.split(";")[3])))
            voltages.append(v)
            capacities.append(q)
        except:
            if '"V";I:"A";C:"Ah/kg"' in line and charge == True:
                #print("Charge end at: V: %.5f, Q: %.5f" %(v,q))
                charges.append((np.array(voltages), np.array(capacities)))
                charge = False
                voltages = []
                capacities = []
            elif '"V";I:"A";C:"Ah/kg"' in line and charge == False:
                #print("Discharge end at: V: %.5f, Q: %.5f" %(v,q))
                discharges.append((np.array(voltages), np.array(capacities)))
                charge = True
                voltages = []
                capacities = []

        
    
    #print(charges)
    #print(discharges)
    return charges, discharges

def read_txt(filepath):
    """
    Reads a txt file to a pandas dataframe

    .txt format:
        line 1: user comment
        header: includes columns TT, U, I, Z1 ++ , corresponding to time, potential, current and cycle number

    Important: In the datafile, in the first line (which is the user description) you must use the keyword CV or GC to tell what type of data it is."""
    import pandas as pd
    import numpy as np
    import os

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
    big_df = pd.read_csv(filepath, header = headerlines-1, sep = "\t")

    #Extract useful columns, change the name of the columns, make all numbers numbers.
    df = big_df[['TT [h]', 'U [V]', 'I [mA]', 'Z1 []', 'C [mAh/kg]']]
    df.rename(columns={'TT [h]': 'time/s', 'U [V]': 'Ewe/V', 'I [mA]': '<I>/mA', 'Z1 []':'cycle number', 'C [mAh/kg]':'capacity/mAhg'}, inplace=True)
    df = df.astype({"time/s": float, "Ewe/V": float, "<I>/mA": float, "capacity/mAhg": float, "cycle number": int})
    df['time/s'] = df['time/s'].apply(lambda x: x*3600) #Converting from h to s
    df['capacity/mAhg'] = df['capacity/mAhg'].apply(lambda x: x*1000) #Convert from mAh/kg to mAh/g
    df['mode'] = 0
    df['charge'] = True
    df.experiment_mode = expmode

    check_df(df)

    return df

def check_df(df):
    """Check if the dataframe has:
    - cycle number (sometimes the Z1 counter fucks up and just says 0)
    - If it is GC data: then calculate capacity
    
    If anything is wrong, it tries to fix it"""


    if df.experiment_mode == 1: #Then its GC
        if df['cycle number'].eq(0).all(): #If all cycle numbers are 0, then maybe Z1 counter was not iterated properly.
            LOG.info("We only found 1 cycle in the data file, and suspect this to be false. Checking now if there should be more cycles.")
            #We fix this by counting our own cycles.

            prev_sign = False
            sign = True #Keeping track of the last sign.
            cycle_number = 1

            for i,current in df['<I>/mA'].items():
                
                if current > 0:
                    sign = True
                    df['charge'].at[i] = True
                elif current < 0:
                    sign = False
                    df['charge'].at[i] = False
                


                if prev_sign is False and sign is True:
                    #Changing from a discharge to a charge means new cycle
                    prev_sign = True
                    cycle_number += 1
                    
                elif prev_sign is True and sign is False:
                    #Changing from a charge to a discharge
                    prev_sign = False

                # In place editing of cycle number
                df['cycle number'].at[i] = cycle_number

                
