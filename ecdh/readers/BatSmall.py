"""Data-readers for Neware"""

from __main__ import LOG
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
    """Main reader for BatSmall data.
    Important: In the datafile, in the first line (which is the user description) you must use the keyword CV or GC to tell what type of data it is."""
    import pandas as pd
    import numpy as np
    import os

    with open(filepath, 'r') as f:
        lines = f.readlines()

    headerlines = 0
    expmode = 0
    for line in lines:
        if "CV" in line or "Cyclic Voltammetry" in line or "cyclic voltammetry" in line:
            expmode = 2
            break
        elif "GC-Step" in line:
            expmode = 1
            break
        else:
            LOG.warning("Cannot find out which type of experiment the file {} is! Please specify either CV or GC in the comment on the top of the file.".format(os.path.basename(filepath)))

    for i,line in enumerate(lines):
        if 'TT' in line and 'U ' in line and 'I ' in line:
            headerlines = i
            break

    big_df = pd.read_csv(filepath, header = headerlines-1, sep = "\t")
    print(big_df)
    df = big_df[['TT [h]', 'U [V]', 'I [mA]', 'Z1 []']]
    df.rename(columns={'TT [h]': 'time/s', 'U [V]': 'Ewe/V', 'I [mA]': '<I>/mA', 'Z1 []':'cycle number'}, inplace=True)
    df['time/s'] = pd.to_numeric(df['time/s'])
    df['Ewe/V'] = pd.to_numeric(df['Ewe/V'])
    df['<I>/mA'] = pd.to_numeric(df['<I>/mA'])
    df['cycle number'] = pd.to_numeric(df['cycle number']).astype('int32')
    df['time/s'] = df['time/s'].apply(lambda x: x*3600) #Converting from h to s
    df['mode'] = 0
    df.experiment_mode = expmode
    print(df)
    return df
