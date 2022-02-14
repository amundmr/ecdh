# -*- coding: utf-8 -*-
"""Data-readers for Neware"""
import os.path
import pandas as pd
import numpy as np      
import gc
from ecdh.log import LOG
LOG.error("MATS IS WORKING ON HANDLING THE DATA FROM THE CSV-FILE TO BE CORRECTLY FORMATED PANDAS.DATAFRAMES")

#skole_fil = "C:/Users/matsarod/OneDrive/Master/Master_oppgave/Batteri_data/MR_T_all/MR_B_test_2.csv"
hjemme_fil = "C:/Users/mats-/OneDrive/Master/Master_oppgave/Batteri_data/MR_T_all/MR_B_test_2.csv"
fil = hjemme_fil
"""
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
"""

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

def time_secs(time_s):
    #Takes neware string of time and returns float in seconds. 
    #Made by AMR. 
    time_s = time_s
    numb = time_s.split(":")
    #day = float(numb[-4])
    hours = float(numb[-3])
    mins = float(numb[-2])
    secs = float(numb[-1])
    time = hours*3600 + mins*60 + secs #+ day*86400 
    return time

def sorting():
    # This function takes out the values from the csv file, handles them, and puts them in the correct lists. 
    # Need to find a way without for-loops with if-statements
    a1,a2,a3,a4,a5,a6 = [3,0,3,0,0,"FALSE_init"]                                         # Initail values
    for k in range(4,len(num)):
        if num[k] == '"':               # Indicates "Extra" --> Gives
            a1 = num[k]                 # Remeber to check if str
            if a1 == 'CC_Chg':
                a1 = 1
                a6 = 'True'
            elif a1 == 'CC_DChg':
                a1 = 2
                a6 = 'False'
            elif a1 == 'Rest':
                a1 = 3
                a6 = 'False'
            else: 
                a1 = 4
                a6 = 'Error'
                
        elif num[k] == '",':            # Indicates "Normal"
            a2 = time_secs(cdc[k])
            a2 = float (a2)    
            a3 = float(scc[k])         
            a4 = float(scd[k])
            
        elif num[k] == '"1':            # Indicates "Main"
            a5 = int(num[k][1][0])      # 
        
        # Here we append the values to correct lists. 
        mode.append(a1) 
        time.append(a2)
        V.append(a3)
        I.append(a4) 
        cyc.append(a5) 
        chrg.append(a6)
        
    sl = [mode,time,V,I,cyc,chrg] 
    return sl

sf = sorting()                                                                  # Calling the sorting function
sl_n = ["mode", "time/s", "Ewe/V", "<I>/A", "cycle number", "charge"]           # The name of the elements in the superlist

# Creating the format of the dataframe we want to have.
df_sl = pd.DataFrame(list(zip(sf[0],sf[1],sf[2],sf[3],sf[4],sf[5])), columns = sl_n)        # Uses zip to flip x/y axis on dataframe
print(df_sl)                                                                               # Printing the final DataFrame with correctly sorted values. Hopefuly



# Output as of 14.02.2022 12:39
"""
   mode  time/s   Ewe/V  <I>/A  cycle number charge
0     3     0.0  2.6742    0.0             0  FALSE
1     3    10.0  2.6739    0.0             0  FALSE
2     3    20.0  2.6739    0.0             0  FALSE
3     3    30.0  2.6736    0.0             0  FALSE
4     3    40.0  2.6736    0.0             0  FALSE
5     3    50.0  2.6736    0.0             0  FALSE
6     3    60.0  2.6729    0.0             0  FALSE
"""