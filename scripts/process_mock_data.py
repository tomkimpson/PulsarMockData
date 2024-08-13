# This script takes in data from the IPTA MDC and generates frequency timeseries
# It outputs two files into the 'output_data/' directory
#   * frequency_timeseries :: a numpy savez object which contains an 'f-tim-file', i.e. frequency timeseries for all pulsars, and an 'f-par-file', i.e. an abridged parameter file for all pulsars
#   * hyper_parameters     :: a json file that records the hyper-parameters used to generate the data

import sys
import glob 
import libstempo.toasim as toasim
import numpy as np
from generate_frequency_timeseries import process_pulsar_files, get_stoas
import libstempo 
import os 
import json
import shutil


# User arguments
seed          = int(sys.argv[1])
gw_amplitude  = float(sys.argv[2])
psr_amplitude = float(sys.argv[3])
efac          = float(sys.argv[4])
ID            = sys.argv[5]        # used for IO
overwrite     = eval(sys.argv[6])

# Define the data to use
path_to_data = '../mdc/IPTA_Challenge1_open/Challenge_Data/Dataset1/'
list_of_par_files = sorted(glob.glob(path_to_data+'/*.par'))
list_of_tim_files = sorted(glob.glob(path_to_data+'/*.tim'))
assert len(list_of_par_files) == len(list_of_tim_files)
Npsr = len(list_of_par_files)

# Define where output data will go
output_dir = f'../output_data/{ID}'

if os.path.exists(output_dir) & overwrite:
    shutil.rmtree(output_dir)
os.mkdir(output_dir)


# Create a dictionary of parameters
# This defines the noise on our synthetic data.
# The dict will be saved to disk that will be saved to disk
dictionary_of_parameters = {'seed': 1,                      # Define a root seed to be used by all random processes
                            'n_gw_sources':int(1e4),        # Number of sources that make up the GWB
                            'gw_amplitude':gw_amplitude,    # Amplitude of GWB
                            'gw_alpha': -2/3,               # Spectral index of GWB
                            'psr_amplitude': psr_amplitude, # Amplitude of pulsar process noise
                            'psr_alpha': 1.7,                 # Spectral index of PSR power law
                            'efac': efac                    # Scaling factor of measurement noise
                            }                 


# Create a GWB object which will be shared between pulsars
# See https://github.com/vallis/libstempo/blob/master/libstempo/toasim.py and https://www.jb.man.ac.uk/~pulsar/Resources/tempo2_examples_ver1.pdf
gwb = toasim.GWB(ngw=dictionary_of_parameters['n_gw_sources'],
                 seed=dictionary_of_parameters['seed'],
                 gwAmp=dictionary_of_parameters['gw_amplitude'],
                 alpha=dictionary_of_parameters['gw_alpha'])



# Initialise two arrays: 
  ##  'f-tim file' that holds the frequency timeseries, 
  ##  'f-par file' that holds the parameters 
  ### Of course, the parameters are also defined in the actual par files, but also useful to have one parameter file that we can load

t = get_stoas(list_of_par_files[0],list_of_tim_files[0])
tim_array = np.zeros((len(t),Npsr+1))   #  Npsr+1 as final column will be time 
par_array = np.zeros((4,Npsr))          # 4 parameters: F0, F1, DEC,RA, in that order


for i in range(Npsr):
    _,f,F0,F1,DEC,RA = process_pulsar_files(par_file      =list_of_par_files[i],
                                            tim_file      =list_of_tim_files[i],
                                            noise_seed    =dictionary_of_parameters['seed']+i, # different seed for each pulsar
                                            gwb           =gwb,
                                            psr_alpha     =dictionary_of_parameters['psr_alpha'],
                                            psr_amplitude =dictionary_of_parameters['psr_amplitude'],
                                            efac          = dictionary_of_parameters['efac'])

     
    tim_array[:,i] = f
    par_array[0,i] = F0
    par_array[1,i] = F1
    par_array[2,i] = DEC
    par_array[3,i] = RA

tim_array[:,-1] = t # last column is time



#Save everything to disk
output_file = f'{output_dir}/frequency_timeseries'
np.savez(output_file, f_tim_file=tim_array, f_par_file=par_array)


# also save the parameters file to disk 
with open(f'{output_dir}/hyper_parameters', 'w') as f: 
    json.dump(dictionary_of_parameters, f)




