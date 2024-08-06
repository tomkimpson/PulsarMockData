import sys 
import glob 
import libstempo
import libstempo.toasim as toasim
import libstempo.plot
import glob
import pandas as pd
import numpy as np

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
    pulsar_emission_times = psr.pets()         # PET for Pulsar Emission Time - these are the ToAs in the pulsar frame
    pulse_number          = psr.pulsenumbers()  # These are the pulse numbers for each ToA --- i.e. the (inferred) absolute phase at each ToA. This is what you really want to use as your phase measurement

    dt = np.diff(pulsar_emission_times)*86400 # PETs are in MJD so multiply by 86400 to get seconds
    dphi = np.diff(pulse_number)
    f = dphi / dt 

    #Consider the frequencies to be evaluated at the lower end of the box - arbitrary
    t_eval = pulsar_emission_times[0:-1]
    assert len(f) == len(t_eval)

    #IO as a pandas df
    df = pd.DataFrame(data={'t': t_eval, 'f': f})
    df.to_pickle(f'../output_data/{psr.name}_frequency_timeseries')

    #also save some meta-data in a separate file. this is sort of equivalent to a par file
    df_meta = pd.DataFrame(data={'pulsar_name':[psr.name], 
                                 'F0': [psr['F0'].val], 
                                 'F1':[psr['F1'].val]})
    df_meta.to_pickle(f'../output_data/{psr.name}_meta_data')






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


for i in range(Npsr):
    process_pulsar(list_of_par_files[i],
                   list_of_tim_files[i],
                   dictionary_of_parameters['seed']+i,
                   gwb,
                   dictionary_of_parameters['psr_alpha'],
                   dictionary_of_parameters['psr_amplitude'])


# Save the parameters file to disk
import json
# e.g. file = './data.json' 
with open('../output_data/hyper_parameters', 'w') as f: 
    json.dump(dictionary_of_parameters, f)