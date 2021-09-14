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