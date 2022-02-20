# -*- coding: utf-8 -*-
"""Data-readers for Neware"""
# Note: If the csv-files are edited in Excel they get " added to the start of the first column. This format change confuses program.
import pandas as pd

# Specified in order to see the all relevant columns of the Dataframe
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)

# Here we define the files we want to use. 
# This should be automated as rest of the code. 
file = "/MR_B_076.csv"         # Real sample. 280 000 lines 

# Filepaths
fp_home = "C:/Users/mats-/OneDrive/Master/Master_oppgave/Batteri_data/MR_T_all"+file
#fp_school = "C:/Users/matsarod/OneDrive/Master/Master_oppgave/Batteri_data/MR_T_all" + file

fil = fp_home
filepath = fil

# Here we introduce the lists that is going to form the dataframe later. 
lead = []               # Indicates Normal/Extra/Main line
mode = []               # mode
time = []               # time/s
V = []                  # Ewe/V
I = []                  # <I>/A
cyc = []                # cycle number
chrg = []               # charge

# List of the names of the columns we need. These names does not represent what values the colummn will have. This is only valid for "Main" 
col_list = ['Cycle ID','Cap_DChg(mAh)','Specific Capacity-Chg(mAh/g)','Specific Capacity-Dchg(mAh/g)']

# This reads the csv file with some extra options
data = pd.read_csv( fil,
                   usecols = col_list,          # Defines which columns you want to collect data from
                   #header=0,                   # Needs to be 0 in order to find the headlines
                   #skiprows = 0,               # Needs to be 0 in order to find the headlines
                   sep=",\t",                   # Removes the odd \t delimiters. Critical.
                   engine='python',             # Don't remeber why I needed this one. Something with calc time?
                   skipinitialspace=True,       # Don't remeber why I needed this one. Something with calc time?
                   #nrows = 60                   # This will chose how many lines you take out from the csv file. Convenient when handling massive files..
                   )                  

# Defining temp list to store untreated data from csv file. 
cdc = data[col_list[1]]          # Colunm marked as "Capacity DisCharge" in csv file
scc = data[col_list[2]]          # Colunm marked as "Specific Capacity Charge" in csv file
scd = data[col_list[3]]          # Colunm marked as "Specific Capacity Discharge" in csv file
num = data[col_list[0]]          # Colunm marked as "Cycle ID" in csv file

def time_secs(time_s):
    #Takes neware string of time and returns float in seconds
    time_s = time_s
    numb = time_s.split(":")
    try:
        day = float(numb[-4])
        hours = float(numb[-3])
        mins = float(numb[-2])
        secs = float(numb[-1])
        time = hours*3600 + mins*60 + secs + day*86400
    except IndexError:
        secs = float(numb[-1])
        time = secs
    return time

def cdr(a4):
    # Function to separate charge/discharge/rest
    # Input (current). Output: Mode, Charging
    ep = 10e-12
    if a4 >= 0+ep:
        a1 = 1
        a6 = 'False'
    elif a4 <= 0-ep:
        a1 = 1
        a6 = 'True'
    elif a4 == 0:
        a1 = 3
        a6 = 'False'
        
    return a1,a6

def sorting():
    # This function takes out the values from the csv file, handles them, and puts them in the correct lists. 
    # Initial values
    a4,a5 = float(scd[3]), int(num[2])
    a1, a2,a3,a6 = cdr(a4)[0], float(time_secs(cdc[4])), float(scc[4]), cdr(a4)[1] 
    
    # The first rows are not included as they are headers. We still need some of them for initail conditons so we can't skip them in the reader.
    for k in range(4,len(num)):
        
        # Adjusting the value of the first cycle after rest
        try:
            q = mode.index(1)+5
            if int(k) == int(q):
                a5 = a5 +1
        except ValueError:
            a5 = 0  
        
        # If we have a cycle number, we make it an integer.
        try:
            a5 = int(num[k])
        # If we the csv column element is ',' it indicates 'Normal' line.
        except ValueError:
            if num[k] == ',':                       # Indicates "Normal"
                b2 = time_secs(cdc[k])
                a2 = float(b2)    
                a3 = float(scc[k])         
                a4 = float(scd[k])
                a1 = cdr(a4)[0]
                a6 = cdr(a4)[1]
        
        # Here we append the  values to its corresponding list. 
        mode.append(a1) 
        time.append(a2)
        V.append(a3)
        I.append(a4)        
        cyc.append(a5) 
        chrg.append(a6) 

    sl = [mode,time,V,I,cyc,chrg]
    return sl

def frame(sl):
    # Making a dataframe from lists. Not general, only made for this purpose. 
    # The name of the elements in the superlist
    sl_n = ["mode", "time/s", "Ewe/V", "<I>/A", "cycle number", "charge"]           
    df_sl = pd.DataFrame(list(zip(sl[0],sl[1],sl[2],sl[3],sl[4],sl[5])), columns = sl_n)
    return df_sl

# Calling the sorting function lists
sfl = sorting()         # Sorted lists

# Calling the dataframe function to make a dataframe out of the sorting function lists
sdf = frame(sfl)        # Sorted dataframe

df_sl0 = sdf.iloc[0:8]
df_sl1 = sdf.iloc[12:18]
df_sl2 = sdf.iloc[6534:6541]
    
print(df_sl0)
print(".....................................................")
print(df_sl1)
print(".....................................................")
print(df_sl2)

#Output as of 20.02.2022
"""
   mode  time/s   Ewe/V  <I>/A  cycle number charge
0     3     0.0  1.0456    0.0             0  False
1     3    10.0  1.0456    0.0             0  False
2     3    20.0  1.0456    0.0             0  False
3     3    30.0  1.0456    0.0             0  False
4     3    40.0  1.0456    0.0             0  False
5     3    50.0  1.0456    0.0             0  False
6     3     0.0  1.0456    0.0             0  False
7     3    10.0  1.0456    0.0             0  False
.....................................................
    mode  time/s   Ewe/V   <I>/A  cycle number charge
12     3     0.0  1.0456  0.0000             0  False
13     3     9.0  1.0456  0.0000             0  False
14     3     9.0  1.0456  0.0000             0  False
15     1     0.0  1.0212 -0.3499             0   True
16     1     4.0  1.0097 -0.3499             1   True
17     1     8.0  0.9988 -0.3499             1   True
.....................................................
      mode  time/s   Ewe/V   <I>/A  cycle number charge
6534     1    50.0  0.0499 -0.3499             1   True
6535     1    50.0  0.0499 -0.3499             2   True
6536     1    50.0  0.0499 -0.3499             2   True
6537     1     0.0  0.0644  0.3500             2  False
6538     1     9.0  0.0747  0.3500             2  False
6539     1    10.0  0.0756  0.3500             2  False
6540     1    20.0  0.0802  0.3500             2  False
"""