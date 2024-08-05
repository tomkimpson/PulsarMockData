import sys 
import glob 
import libstempo
import libstempo.toasim as toasim
import libstempo.plot
import glob

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
    


# Define the data to use
path_to_data = '../mdc/IPTA_Challenge1_open/Challenge_Data/Dataset1/'
list_of_par_files = sorted(glob.glob(path_to_data+'/*.par'))
list_of_tim_files = sorted(glob.glob(path_to_data+'/*.tim'))
assert len(list_of_par_files) == len(list_of_tim_files)
Npsr = len(list_of_par_files)


# Define a root seed to be used by all random processes
root_seed = 1

#Create a GWB object which will be shared between pulsars
# See https://github.com/vallis/libstempo/blob/master/libstempo/toasim.py and https://www.jb.man.ac.uk/~pulsar/Resources/tempo2_examples_ver1.pdf
n_gw_sources = int(1e3)
gw_amplitude = 1e-15
gw_alpha = -2/3
gwb = toasim.GWB(ngw=n_gw_sources,seed=root_seed,gwAmp=gw_amplitude,alpha=gw_alpha)

# Defin psr red noise parameters
# These are the same for all pulsars
psr_alpha = 4 
psr_amplitude = 1e-12


for i in range(Npsr):
    process_pulsar(list_of_par_files[i],list_of_tim_files[i],root_seed+i,gwb,psr_alpha,psr_amplitude)
    sys.exit()