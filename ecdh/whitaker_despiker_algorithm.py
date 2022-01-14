#Author: Nicolai Haaber Junge

import numpy as np
from scipy import stats

def Modified_Zscore(y, x):
    """
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

def Whitaker_Despiker(y, z_score, threshold=4, ma=5):
    """
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