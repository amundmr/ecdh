from textwrap import TextWrapper
import os

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

preferredWidth = 70

def error(message):
    prefix = f"{bcolors.FAIL}[ERROR]{bcolors.ENDC} "

    wrapper = TextWrapper(initial_indent=prefix, width=preferredWidth,
                               subsequent_indent=' '*(len(prefix)-len(f'{bcolors.FAIL}{bcolors.ENDC}')))

    print(wrapper.fill(message))

def warn(message):
    prefix = f"{bcolors.WARNING}[WARNING]{bcolors.ENDC} "
    wrapper = TextWrapper(initial_indent=prefix, width=preferredWidth,
                               subsequent_indent=' '*(len(prefix)-len(f'{bcolors.WARNING}{bcolors.ENDC}')))
    print(wrapper.fill(message))

def info(message):
    prefix = f"{bcolors.OKCYAN}[INFO]{bcolors.ENDC} "
    wrapper = TextWrapper(initial_indent=prefix, width=preferredWidth,
                               subsequent_indent=' '*(len(prefix)-len(f'{bcolors.OKCYAN}{bcolors.ENDC}')))
    print(wrapper.fill(message))


def check_files(list):
    # Checks that files exist and then returns the ones that does.
    return_list = []
    for file in list:
        filename = file[0]
        if os.path.isfile(filename):
            return_list.append(file)
        else:
            error("File not found: '" + str(filename) + "' Please check that the correct path is typed in your input toml file. Skipping this file.")
    return return_list

def simplify(chg, dchg):
    # Takes two lists of complete cycle data and returns max capacity for each cycle.
    # chg = [cycle1, cycle2, cycle3 , ... , cycleN]
    # cycle1 = [[v1, v2, v3, ..., vn],[q1, q2, q3, ..., qn]]
    # This func basically just pulls qn from every cycle and creates a new array with it.
    import numpy as np

    charges = np.zeros(len(chg))
    discharges = np.zeros(len(dchg))
    for i, cycle in enumerate(chg):
        try:
            charges[i] = cycle[1][-1]
        except:
            charges[i] = 0
    for i, cycle in enumerate(dchg):
        try:
            discharges[i] = cycle[1][-1]
        except:
            discharges[i] = 0
    return charges, discharges

def make_dQdV(chg, dchg, nbins = 200):
    # chg = [cycle1, cycle2, cycle3 , ... , cycleN]
    # cycle1 = [[v1, v2, v3, ..., vn],[q1, q2, q3, ..., qn]]
    import numpy as np

    bins = np.linspace(chg[0][0][0],chg[0][0][-1],nbins)

    chg_new = []
    dchg_new = []
    for cyc, dcyc in zip(chg,dchg):
        cyc_dqdvs = []
        dcyc_dqdvs = []
        for i in range(len(bins)-1):
            #print("Bin start: %.2f stop: %.2f" %(bins[i], bins[i+1]))
            start_indx = (np.abs(cyc[0] - bins[i])).argmin()
            end_indx = (np.abs(cyc[0] - bins[i+1])).argmin()
            #print("start indx: %i, stop indx: %i" % (start_indx, end_indx))
            cyc_dQdV = (cyc[1][end_indx]-cyc[1][start_indx]) / (cyc[0][end_indx] - cyc[0][start_indx])

            start_indx = (np.abs(dcyc[0] - bins[i])).argmin()
            end_indx = (np.abs(dcyc[0] - bins[i+1])).argmin()
            #print("start indx: %i, stop indx: %i" % (start_indx, end_indx))
            dcyc_dQdV = (dcyc[1][end_indx]-dcyc[1][start_indx]) / (dcyc[0][end_indx] - dcyc[0][start_indx])

            cyc_dqdvs.append(cyc_dQdV)
            dcyc_dqdvs.append(dcyc_dQdV)

        chg_new.append((bins[:-1],(np.asarray(cyc_dqdvs))))
        dchg_new.append((bins[:-1],(np.asarray(dcyc_dqdvs))))

    
    return chg_new, dchg_new

def make_label(ncycle):
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    return str(ordinal(ncycle)) + " cycle"