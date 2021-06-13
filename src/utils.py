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
        charges[i] = cycle[1][-1]
    for i, cycle in enumerate(dchg):
        discharges[i] = cycle[1][-1]
    return charges, discharges