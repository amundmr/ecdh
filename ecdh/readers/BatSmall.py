"""Data-readers for Neware"""

from __main__ import LOG
LOG.error("BATSMALL READER HAS NOT BEEN MOVED OVER TO PD DATAFRAMES")
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

def read_dat(filepath):
    import pandas as pd
    import numpy as np
    
    with open(filepath, 'r') as f:
        lines = f.readlines()

    headerlines = 0
    expmode = 0
    for line in lines:
        if "CV-Step" in line:
            expmode = 2
            break
        elif "GC-Step" in line:
            expmode = 1
            break

    for i,line in enumerate(lines):
        if '"V";I:"A";C:"Ah/kg"' in line:
            headerlines = i

    big_df = pd.read_csv(filepath, header = headerlines, sep = ";")

    df = big_df[['7HU:"V"', 'I:"A"']]
    df.rename(columns={'7HU:"V"': 'Ewe/V', 'I:"A"': '<I>/mA'}, inplace=True)
    df['Ewe/V'] = pd.to_numeric(df['Ewe/V'])
    df['<I>/mA'] = pd.to_numeric(df['<I>/mA'])
    df['<I>/mA'] = df['<I>/mA'].apply(lambda x: x*1000) #Converting from A to mA
    df['time/s'] = 0
    df['mode'] = 0
    df['cycle number'] = 0
    df.experiment_mode = expmode
    print(df)
    return df
