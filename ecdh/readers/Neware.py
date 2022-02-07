# -*- coding: utf-8 -*-
"""Data-readers for Neware"""
import os.path
import pandas as pd
import numpy as np      
import gc
from ecdh.log import LOG
LOG.error("MATS IS WORKING ON HANDLING THE DATA FROM THE CSV-FILE TO BE CORRECTLY FORMATED PANDAS.DATAFRAMES")

skole_fil = "C:/Users/matsarod/OneDrive/Master/Master_oppgave/Batteri_data/MR_T_all/MR_B_test_2.csv"
hjemme_fil = "C:/Users/mats-/OneDrive/Master/Master_oppgave/Batteri_data/MR_T_all/MR_B_test_2.csv"

def find_path():
    # Function to sort out if home PC or school PC. 
    # This have improvement potential. 
    # This takes some time to check, but nice to have since I'm on two computers.
    if os.path.isfile(skole_fil) == False:
        fil = hjemme_fil
    else: 
        fil = skole_fil

    #Check if the filepath exists: 
    print("Filepath exists =",os.path.isfile(fil))
    print("")


def read_csv(filepath):
    LOG.error("This is under development.")

# Here we introduce the lists that is going to form the dataframe later. 
mode = []               # mode
time = []               # time/s
V = []                  # Ewe/V
I = []                  # <I>/A
cyc = []                # cycle number
chrg = []               # charge


# List of the names of the columns we need. These names does not represent what values the colummn will have. This is only valid for "Main" 
col_list = ['"Cycle ID', "Cap_DChg(mAh)", "Specific Capacity-Chg(mAh/g)", "Specific Capacity-Dchg(mAh/g)"]

# This reads the csv file with some extra options
data = pd.read_csv( fil,
                   usecols = col_list,          # Defines which columns you want to collect data from
                   #header=0,                   # Needs to be 0 in order to find the headlines
                   #skiprows = 0,               # Needs to be 0 in order to find the headlines
                   sep=",\t",                   # Removes the odd \t delimiters. Critical.
                   engine='python',             # Don't remeber why I needed this one. Something with calc time?
                   skipinitialspace=True,       # Don't remeber why I needed this one. Something with calc time?
                   #nrows = 5                   # This will chose how many lines you take out from the csv file. Convenient when handling large files..
                   )                  

# Defining temp list to store untreated data from csv file. 
cdc = data[col_list[1]]          # Colunm marked as "Capacity DisCharge" in csv file
scc = data[col_list[2]]          # Colunm marked as "Specific Capacity Charge" in csv file
scd = data[col_list[3]]          # Colunm marked as "Specific Capacity Discharge" in csv file
num = data[col_list[0]]          # Colunm marked as "Cycle ID" in csv file

wl = [cdc, scc, scd, num]        # This is the master working list which is going to store the raw colouns before they are sorted.

def mode():
    # This functions can be used in order to identify what kind of column format we are working with. 
    for i in range(len(num)):
        if num[i] == '"':          # Indicates "Extra" --> Gives
            print("Extra")
            print(num[i])
        elif num[i] == '",':         # Indicates "Normal"
            print(num[i])
            print("Normal")
        elif num[i] == '"1':        # Indicates "Main"
            print("Main")
            print(num[i])
        elif num[i] == '",,':       # Indicates "Unknown"
            print("Ukjent")
            print(num[i])
        else: 
            print("ups")
        print("")

# We don't need this, so we take we don't call it.             
#mode()

# We set some reasonable conditions so that we have an equal amout of 
# Initial conditions: 
a1 = 3              # mode_0 = 3        (rest)                      Float/Int
a2 = 0              # Time_0 = 0        (sekunder)                  Float/Int
a3 = 3.00           # V_0 = 3.00        (V, OCV)                    Float
a4 = 0.000          # I_0 = 0.0         (current at rest)           Float   
a5 = 0              # cyc_0 =           (rest cyc = 0)              Float/Int
a6 = "FALSE"        # chrg = FALSE      (True/False if charging)    str ?    

def sorting():
    # This function takes out the values from the csv file, handles them, and puts them in the correct lits. 
    # Need to find a way without for-loops with if-statements. 
    # Not finished. 
    for k in range(len(num)):
        
        if num[k] == '"':               # Indicates "Extra" --> Gives
            b1 = num[k]                 # Remeber to check if str
            if b1 == 'CC_Chg':
                a1 = 1
                a6 = 'True'
            elif b1 == 'CC_DChg':
                a1 = 2
                a6 = 'False'
            elif b1 == 'Rest':
                a1 = 3
                a6 = 'False'
            else: 
                a1 = 99
                a6 = 'Error'
                
        elif num[k] == '",':            # Indicates "Normal"
            a2 = cdc[k]                 # Needs to be a float of seconds
            a3 = (scc[k])         
            a4 = (scd[k])        
            #a3 = float(scc[k])         # Check if float
            #a4 = float(scd[k])         # Check if float
            
        elif num[k] == '"1':            # Indicates "Main"
            a5 = int(num[k][1][0])      # 
    
    
    
    print('a1 =', a1, 'a2=', a2, 'a3 =', a3, 'a4 =', a4,'a5 =', a5, 'a6 =', a6)

# We print out the types of our last list element. 
print( type(a1), type(a2), type(a3), type(a4), type(a5), type(a6), )

# I need to sort out the lists correct before making a dataframe out of them. 
# With test-numbers the format of the dataframe is correct. Need to job some on the lists. 
""" 
    # Here we append the values to correct lists. 
    mode.append(a1) 
    time.append(a2)
    V.append(a3)
    I.append(a4) 
    cyc.append(a5) 
    chrg.append(a6)

sl = [mode,time,V,I,cyc,chrg]                                                   # Superlist consisting of all the important lists
sl_n = ["mode", "time/s", "Ewe/V", "<I>/A", "cycle number", "charge"]           # The name of the elements in the superlist.
#print(sl)                                                                      # print the superlist to check. 

# Creating the format of the dataframe we want to have.
df_sl = pd.DataFrame(list(zip(mode,time,V,I,cyc,chrg)), columns = sl_n)         # Uses zip to flip x/y axis on dataframe
print(df_sl)                                                                    # Printing the final DataFrame with correctly sorted values. Hopefuly
"""

# Output as of 07.02.2022 12:27
"""
a1 = 99 a2= 0 a3 = 3.0 a4 = 0.0 a5 = 0 a6 = Error
a1 = 99 a2= Time(h:min:s.ms) a3 = Voltage(V) a4 = Current(mA) a5 = 0 a6 = Error
a1 = 99 a2= Time(h:min:s.ms) a3 = Voltage(V) a4 = Current(mA) a5 = 1 a6 = Error
a1 = 99 a2= Time(h:min:s.ms) a3 = Voltage(V) a4 = Current(mA) a5 = 1 a6 = Error
a1 = 99 a2= 0:00:00.000 a3 = 2.6742 a4 = 0.0000 a5 = 1 a6 = Error
a1 = 99 a2= 0:00:10.000 a3 = 2.6739 a4 = 0.0000 a5 = 1 a6 = Error
a1 = 99 a2= 0:00:20.000 a3 = 2.6739 a4 = 0.0000 a5 = 1 a6 = Error
a1 = 99 a2= 0:00:30.000 a3 = 2.6736 a4 = 0.0000 a5 = 1 a6 = Error
a1 = 99 a2= 0:00:40.000 a3 = 2.6736 a4 = 0.0000 a5 = 1 a6 = Error
a1 = 99 a2= 0:00:50.000 a3 = 2.6736 a4 = 0.0000 a5 = 1 a6 = Error
a1 = 99 a2= 0:01:00.000 a3 = 2.6729 a4 = 0.0000 a5 = 1 a6 = Error
<class 'int'> <class 'str'> <class 'str'> <class 'str'> <class 'int'> <class 'str'>
"""














# From Amund's code. Will probably steal this. 
"""
def _time_parser(string):
        #Takes neware string of time and returns float in seconds
        print(string)
        string = string[2:]
        nums = string.split(":")
        hours = float(nums[0])
        mins = float(nums[1])
        secs = float(nums[2])
        return hours*3600 + mins*60 + secs

"""

# The old code. 
"""
def read_csv_old(filepath):

    #Reads a .csv file from Neware general report
    
    #.csv format:
    
    
    LOG.debug(f"Reading Neware CSV: '{filepath}'")

    # Open file
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Read all data to pandas dataframe
    big_df = pd.read_csv(filepath, header = 2, delim_whitespace=True)
    pd.DataFrame.fillna(big_df, method='ffill', inplace = True)
    #print(big_df["Unnamed: 0"].head)
    print(big_df.columns)
    print(big_df.head)
    #df = big_df.loc[:,('\tTime(h:min:s.ms)', '\tVoltage(V)', '\tCurrent(mA)', 'Unnamed: 0', '\tCapacity Density(mAh/g)')]
    del big_df #deletes the dataframe
    gc.collect() #Clean unused memory (which is the dataframe above)
    #print(df.head)
    #df.columns = ['time/s','Ewe/V', '<I>/mA', 'cycle number', 'capacity/mAhg'] 
    #print(df.columns)
    #print(df['time/s'].iloc[1])
    def _time_parser(string):
        #Takes neware string of time and returns float in seconds
        print(string)
        string = string[2:]
        nums = string.split(":")
        hours = float(nums[0])
        mins = float(nums[1])
        secs = float(nums[2])
        return hours*3600 + mins*60 + secs

    df['time/s'] = df['time/s'].apply(lambda x: _time_parser(x)) #Converting from h to s
    print(df.head)

"""

    """import numpy as np
    #Open file
    with open(filepath, 'r', encoding = "ISO-8859-1") as f:
        #Read the first 2 lines which doesnt contain any data
        for i in range(2):
            f.readline()

        #Find what columns have our data
        Labels = f.readline().split(",") #Save the line of labels of which we are interested in
        V_col = 0
        mAh_col = 0
        for i,label in enumerate(Labels):
            if "Voltage(V)" in label:
                V_col = i
            if "Capacity(mAh)" in label:
                mAh_col = i

        #Read rest of data as list of lines
        data = f.readlines()
    
    #Index where in the file charges and discharges occur
    Chg_indxs = []
    DChg_indxs = []

    for i,line in enumerate(data):
        line_split = line.split(",")
        if "CC_Chg" in line_split[2]:
            Chg_indxs.append(i)
        elif "CC_DChg" in line_split[2]:
            DChg_indxs.append(i)

    charges = []
    discharges = []
    #Returns two arrays with Voltage and Capacity for the selected indexes of data.
    def slice_data(start, end, data):
        if end == -1:
            end = len(data)

        #Spawning data arrays
        start +=1
        end -=2
        voltages = np.zeros(end-start)
        capacities = np.zeros_like(voltages)
        for j,line in enumerate(data[start: end]):#Taking the slice of the data arr
            line = line.split(",")
            voltages[j] = float(line[V_col])
            capacities[j] = float(line[mAh_col])
        return voltages, capacities

    #Create one big list of all indexes in order to know which one is the next
    all_indxs = Chg_indxs + DChg_indxs
    all_indxs.sort()
    # Iterating over all indexes of charge start
    for i, indx in enumerate(Chg_indxs):
        i_all = all_indxs.index(indx) #Finding the corresponding item in list of all indexes
        start = indx   #Setting start of Charge to the charge index
        try:            #Setting end of charge to discharge index, or last index of data.
            end = all_indxs[i_all+1]
        except:
            end = len(data)-1
        #Getting the data slice, and putting it in charges list.
        voltages, capacities = slice_data(start, end, data)
        #print(voltages)
        charges.append((voltages, capacities))
    
    # Iterating over all indexes of discharge start
    for i, indx in enumerate(DChg_indxs):
        i_all = all_indxs.index(indx) #Finding the corresponding item in list of all indexes
        start = indx   #Setting start of Discharge to the discharge index
        try:            #Setting end of charge to charge index, or last index of data.
            end = all_indxs[i_all+1]
        except:
            end = len(data)-1
        #Getting the data slice, and putting it in charges list.
        voltages, capacities = slice_data(start, end, data)
        discharges.append((voltages, capacities))

            
    return charges, discharges"""