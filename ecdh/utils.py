
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


def moving_average(x, w):
    import numpy as np
    y_padded = np.pad(x, (w//2, w-1-w//2), mode='edge')
    y_smooth = np.convolve(y_padded, np.ones((w,))/w, mode='valid') 
    return y_smooth


def smooth(y,x, threshold = 0.1, ma=100):
    import numpy as np
    from scipy import stats

    def _modified_zscore(y, x):
        
        """
        Author: Nicolai Haaber Junge
        Calculated the z-score from y-data used in the whittaker
        despiker algorithm: whittaker_despiker().
        ----------------
        INPUTS:
        y . numpy vector array with intensity data.
        x : numpy vector array with positional data.
        ----------------
        RETURNS:
        z_score : Modified Z-score of the y intensity data.
        x[:-1] : Shortened x-data as the len(z_score) = len(y difference array)
        ----------------
        """
        ydiff = np.diff(y)  # Calculates difference vector of y
        m = np.median(ydiff) 
        M = stats.median_abs_deviation(ydiff, scale='normal') # Median abs deviation, 75th percentile
        z_score = (ydiff - m)/M  #Z-score
        return z_score, x[:-1]

    def _whitaker_despiker(y, z_score, threshold, ma):
        """
        Author: Nicolai Haaber Junge
        Implementation of the Whitaker & Hayes[1] modified Z-score despiking algorithm
        originally for Raman spectra.
        [1] Whitaker, D.; Hayes, K.. A Simple Algorithm for Despiking Raman Spectra, 2018
            https://doi.org/10.26434/chemrxiv.5993011.v2.
            
        The greater the threshold value the less sensitive the despiking will be.
        A greater "ma" value gives a larger span of datapoints for determining an average intensity 
        for filling in the data where the spike was removed.
        
        Generally spikes are easily removed but if the spikes start to appear like peaks the results
        may not be perfect.
        
        It is generally a good idea to plot x vs z_score and x vs z_spikes to select a good a threshold value. 
        
        Example:
        
        y_data = df['Intensity'].to_numpy()  #Using a pandas dataframe
        x_data = df['Wavenumbers'].to_numpy()  #Using a pandas dataframe
        
        z_score, x_data_new = Modified_Zscore(y_data, x_data)
        y_despiked, z_spikes = Whitaker_Despiker(y_data, z_score, threshold=6, ma=5)
        ---------------
        INPUTS:
        y : numpy vector with intensity data
        z_score : numpy vector with z_scores from modified_zscore()
        ---------------
        RETURNS:
        y_out : despiked intensity vector
        z_spikes : Z spiked vector of zeros and ones.
        """
        y = y[:-1]  #Removing last data point as z is based in the y difference array
        z_spikes = (np.abs(z_score) > threshold)*1  #Generates vector with 0s and 1s where 1s are index positions of spikes
        n = len(y)
        y_out = y.copy() 
        z_spikes[0], z_spikes[n-1] = 1, 1
        spikes = np.where(z_spikes == 1)[0]
        for i in spikes:
            w = np.arange(np.maximum(1, i-ma), np.minimum(n, i+ma))  # Span of data points covering spikes regions
            w = w[z_spikes[w] == 0]  # Selecting non-spiked data points
            y_out[i] = np.mean(y[w]) # Setting spiked intensity equal to average of non-spiked data in the vicinity of the spikes

        return y_out, z_spikes

    z_score, x = _modified_zscore(y, x)
    y_out, z_spikes = _whitaker_despiker(y, z_score, threshold, ma)
    return y_out, x