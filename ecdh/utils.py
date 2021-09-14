
import os


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