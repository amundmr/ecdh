class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def warn(message):
    print(f"{bcolors.WARNING}[WARNING]{bcolors.ENDC} " + message)

def info(message):
    print(f"{bcolors.OKCYAN}[INFO]{bcolors.ENDC} " + message)

def simplify(chg, dchg):
    # Takes two lists of complete cycle data and returns max capacity for each cycle.
    # chg = [cycle1, cycle2, cycle3 , ... , cycleN]
    # cycle1 = [[v1, v2, v3, ..., vn],[q1, q2, q3, ..., qn]]
    # This func basically just pulls qn from every cycle and creates a new array with it.
    import numpy as np
    lnth = len(chg)
    charges = np.zeros(lnth)
    discharges = np.zeros(lnth)
    for i, cycle in enumerate(chg):
        charges[i] = cycle[1][-1]
    for i, cycle in enumerate(dchg):
        discharges[i] = cycle[1][-1]
    return charges, discharges