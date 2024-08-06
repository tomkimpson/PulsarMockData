import sys 
import glob 
import libstempo
import libstempo.toasim as toasim
import libstempo.plot
import glob
import pandas as pd
import numpy as np



# This script takes in data from the IPTA MDC and generates frequency timeseries
# It outputs two files into the 'output_data/' directory
#   * frequency_timeseries :: a numpy savez object which contains an 'f-tim-file', i.e. frequency timeseries for all pulsars and an 'f-par-file', i.e. an abridged parameter file for all pulsars
#   * hyper_parameters :: a json file that records the hyper-parameters used to generate the data




def get_stoas(par_file,tim_file):
    #Create a pulsar object   
    psr = libstempo.tempopulsar(parfile=par_file,timfile=tim_file)   
    stoas = psr.stoas
    t_seconds = (stoas-stoas[0])*86400 # make first time =0, and convert everything to seconds

    return t_seconds[:-1] # drop the final time since f is defined via t2-t1 and so len(f) = len(t) - 1


def process_pulsar(par_file,tim_file,noise_seed,gwb,psr_alpha,psr_amplitude):

    #Create a pulsar object
   
    psr = libstempo.tempopulsar(parfile=par_file,timfile=tim_file)   
    print(f'Processing pulsar {psr.name}')

    #make_ideal shifts the ToAs so that they are exactly aligned with the timing model we loaded
    toasim.make_ideal(psr) 
    toasim.make_ideal(psr) # For whatever reason doing two passes of make_ideal gets a better result - with just one you can end up with a slight trend in the residuals


    #add noise
    toasim.add_rednoise(psr,psr_amplitude,psr_alpha,seed=noise_seed)     # Add some red noise 
    toasim.add_efac(psr,seed=noise_seed)                                 # Add white noise at the level specified in the .tim file. For dataset 1 this is the same for all pulsars. Note that for dataset 2 this is not true - different pulsars have different TOA errs
    gwb.add_gwb(psr,1) # Add GW background noise. Assumes all pulsars are at 1kpc
    

    #Convert to frequency
    pulsar_emission_times = psr.pets()          # PET for Pulsar Emission Time - these are the ToAs in the pulsar frame
    pulse_number          = psr.pulsenumbers()  # These are the pulse numbers for each ToA --- i.e. the (inferred) absolute phase at each ToA. This is what you really want to use as your phase measurement

    dt = np.diff(pulsar_emission_times)*86400 # PETs are in MJD so multiply by 86400 to get seconds
    dphi = np.diff(pulse_number)
    f = dphi / dt 


    return f,psr.name,psr['F0'].val,psr['F1'].val,psr['DECJ'].val,psr['RAJ'].val








# Define the data to use
path_to_data = '../mdc/IPTA_Challenge1_open/Challenge_Data/Dataset1/'
list_of_par_files = sorted(glob.glob(path_to_data+'/*.par'))
list_of_tim_files = sorted(glob.glob(path_to_data+'/*.tim'))
assert len(list_of_par_files) == len(list_of_tim_files)
Npsr = len(list_of_par_files)


# Create a dictionary of parameters
# This defines our synthetic data.
# The dict will be saved to disk that will be saved to disk
dictionary_of_parameters = {'seed': 1,                  # Define a root seed to be used by all random processes
                            'n_gw_sources':int(1e3),
                            'gw_amplitude':5e-14,
                            'gw_alpha': -2/3,
                            'psr_alpha': 4, 
                            'psr_amplitude': 0.0} # Dataset 1 has zero PSR red noise. Lets try this easy case first


#Create a GWB object which will be shared between pulsars
# See https://github.com/vallis/libstempo/blob/master/libstempo/toasim.py and https://www.jb.man.ac.uk/~pulsar/Resources/tempo2_examples_ver1.pdf
gwb = toasim.GWB(ngw=dictionary_of_parameters['n_gw_sources'],
                 seed=dictionary_of_parameters['seed'],
                 gwAmp=dictionary_of_parameters['gw_amplitude'],
                 alpha=dictionary_of_parameters['gw_alpha'])



# Define 2 arrays: one 'f-tim file' that holds the frequency timeseries, one 'f-par file' that holds the parameters 
# Of course, the parameters are also defined in the actual par files, but also useful to have one parameter file that we can load


# I am going to assume that the time at which each f(t) is evaluated is the same for each pulsar
# This seems like a reasonable assumption - but there may be something subtle here that I am missing. 
# Important to check this
t = get_stoas(list_of_par_files[0],
              list_of_tim_files[0]
             )

# f-tim outout array
tim_array = np.zeros((len(t),Npsr+1)) # Npsr+1 as final column will be time 
tim_array[:,-1] = t

# f-par outout array
par_array = np.zeros((4,Npsr)) # 4 parameters: F0, F1, DEC,RA, in that order

for i in range(Npsr):
    f,psr_name,F0,F1,DEC,RA = process_pulsar(list_of_par_files[i],
                   list_of_tim_files[i],
                   dictionary_of_parameters['seed']+i,
                   gwb,
                   dictionary_of_parameters['psr_alpha'],
                   dictionary_of_parameters['psr_amplitude'])
    
    tim_array[:,i] = f
    par_array[0,i] = F0
    par_array[1,i] = F1
    par_array[2,i] = DEC
    par_array[3,i] = RA


#Save everything to disk
output_file = '../output_data/frequency_timeseries'
np.savez(output_file, f_tim_file=tim_array, f_par_file=par_array)


# also save the parameters file to disk 
import json
with open('../output_data/hyper_parameters', 'w') as f: 
    json.dump(dictionary_of_parameters, f)




