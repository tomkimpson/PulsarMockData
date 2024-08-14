# Module which defines a few functions for processing .tim and .par files and generating frequency timeseries
import sys 
import glob 
import libstempo
import libstempo.toasim as toasim
import libstempo.plot
import glob
import pandas as pd
import numpy as np


def process_pulsar_files(par_file,tim_file,noise_seed,gwb,psr_alpha,psr_amplitude,efac):

    """
    A function to produce frequency timeseries from a .par and .tim file


    Arguments:
        par_file:      a standard pulsar .par file
        tim_file:      a standard pulsar .tim file
        noise_seed:    an integer which seeds the process and measurement stochastic processes 
        gwb:           a GW background object from libstempo. See See https://github.com/vallis/libstempo/blob/master/libstempo/toasim.py and https://www.jb.man.ac.uk/~pulsar/Resources/tempo2_examples_ver1.pdf
        psr_alpha:     the spectral index of the PSR process noise
        psr_amplitude: the amplitude of the PSR process noise
        efac:          a scaling factor which scales the measurement errors recorded in the .tim file

    Returns:

        t_eval: array of times in seconds, starting from t=0
        f_Hz:   array of (ephemeris subtracted) frequencies in Hz
        F0:     pulsar spin frequency at t=0
        F1:     pulsar spin frequency derivative at t=0 
        DECJ:   pulsar declination, radians
        RAJ:    pulsar right ascension, radians 

    """

    #Create a pulsar object
    psr = libstempo.tempopulsar(parfile=par_file,timfile=tim_file)   
    psr['TRACK'].val = -2
    print(f'Processing pulsar {psr.name}')

    # Shift the ToAs so that they are exactly aligned with the timing model we loaded
    # For whatever reason doing two passes of make_ideal gets a better result - with just one you can end up with a slight trend in the residuals
    toasim.make_ideal(psr) 
    toasim.make_ideal(psr) 


    #Add noise
    toasim.add_rednoise(psr,psr_amplitude,psr_alpha,seed=noise_seed)     # Add some red noise 
    gwb.add_gwb(psr,1)                                                   # Add GW background noise. Assumes all pulsars are at 1kpc
    f_Hz_no_measurement_noise = convert_to_frequencies(psr)              # Generate a frequency timeseries for this object before we add white measurement noise
    toasim.add_efac(psr,seed=noise_seed,efac=efac)                       # Add white noise at the level specified in the .tim file. For dataset 1 this is the same for all pulsars. Note that for dataset 2 this is not true - different pulsars have different TOA errs
    f_Hz = convert_to_frequencies(psr)                                    # Generate a frequency timeseries including measurement noise

    

    #Get times at which the frequencies were evaluated
    #We consider the frequencies to be evaluated at the lower end of the box - arbitrary
    t_eval = get_stoas(par_file,tim_file) # Alternatively, t_eval = pulsar_emission_times[0:-1]. I don't think the difference matters, but we should double check

    #Assuming all pulsars have a timing measurement noise of 0.1 mu s (true for dataset 1), estimate the uncertainty on the frequency measurement
    σm = 0.1*1e-6 *  psr['F0'].val / (t_eval[1] - t_eval[0])


    return t_eval,f_Hz_no_measurement_noise,f_Hz,psr['F0'].val,psr['F1'].val,psr['DECJ'].val,psr['RAJ'].val, σm




def convert_to_frequencies(psr_object):
    """
    Given a libstempo psr object, return a frequency timeseries 
    """
 
    #Get residuals and PETs
    residuals             = psr_object.residuals()                         # units of seconds
    pulsar_emission_times = (psr_object.pets()-psr_object.pets()[0])*86400 # PET for Pulsar Emission Time - these are the ToAs in the pulsar frame. PETs are in MJD so multiply by 86400 to get seconds

    #Get differences
    dt = np.diff(pulsar_emission_times)
    dres = np.diff(residuals)
    
    #Get frequency
    f    = dres / dt 
    f_Hz = f*psr_object['F0'].val # F0 factor for units 

    return f_Hz





def get_stoas(par_file,tim_file):
    """At what time should we consider the frequencies to be evaluated?"""
    #Create a pulsar object   
    psr = libstempo.tempopulsar(parfile=par_file,timfile=tim_file)   
    stoas = psr.stoas
    t_seconds = (stoas-stoas[0])*86400 
    return t_seconds[:-1] # drop the final time since f is defined via t2-t1 and so len(f) = len(t) - 1

