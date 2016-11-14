from netCDF4 import Dataset
import numpy as np
import glob
import sys
import forwardmodel

yyyymmdd = sys.argv[1]

# Load in the AERI and MWR and radiosonde data for a specific day

aeri_dir = '/raid/FRDD/Dave.Turner/data/clamps/clamps1/'
mwr_dir = './'
sonde_dir = '/raid/FRDD/Dave.Turner/data/norman/sonde/netcdf/'

# pair up files 
aeri_files = np.sort(glob.glob(

