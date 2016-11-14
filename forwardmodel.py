import subprocess
import numpy as np
import os
import sys
import pylblrtm
import glob
from netCDF4 import Dataset



def LBLRTM(sonde_file):
    d = Dataset(sonde_file)
    temp = d.variables['tdry'][:]
    rh = d.variables['rh'][:]
    h = d.variables['alt'][:]
    p = d.variables['pres'][:]
    
    q = pylblrtm.tape5_writer.rh2w(rh, p, temp)[0]    
    ZNBD = np.concatenate((np.arange(11)*0.1,np.arange(10)*0.25+1.25,\
                            np.arange(23)*0.5+4.0,np.arange(5)+16, np.arange(10)*2+22, np.arange(8)*4+42)) 
    
    # Interpolate to the LBLRTM GRID
    h = (h - h[0])/1000.
    #temp = np.interp(ZNBD, h, temp)
    #q = np.interp(ZNBD,h, q)
    #p = np.interp(ZNBD,h, p)
    
    # Tell LBLRTM to output AERI radiance and use radiosonde profile. 
    pylblrtm.tape5_writer.makeFile('tp5', 400,1800, MODEL=0, IEMIT=1, HMOL_VALS=[1,395e-6,1,1,1,1,1],\
                                   tmpc=temp, pres=p, hght=h, wvmr=q, ISCAN=3, IXSECT=1)    
    

def monoRTM(sonde_file, debug=False):
    '''
        gen_Fx

        This function runs the MonoRTM given a frequency file, a config file, a sonde file,
        and any additional parameters the MonoRTM needs.  It outputs a vector of brightness
        temperature values for different frequencies.

        Parameters
        ----------
        sonde_file : a string that contains the path to the netCDF sonde file to be run by MonoRTM

        Returns
        -------
        F_x : the F_x brightness temperature vector
    '''

    # Set MonoRTM adaptable parameters.
    pwv_sf = "1.0" # PWV scale factor is 1

    Fx = None
    elevs = None
    freqs = None
    os.system('chmod 744 mwr_retr_monortm_config_66L.txt')
    os.environ['monortm_config'] = 'mwr_retr_monortm_config_66L.txt'

    elevations = [90]
    f = 'mwr_retr_monortm_freqs.zen'
    # Set the monortm_freqs environment variable
    os.system ("chmod 744" + " " + f)
    os.environ['monortm_freqs'] = f
    
    # Build the string to be used to run MonoRTM on the command line 
    monoStr = ['monortm_v4', sonde_file]#, pwv_sf, LWP, cbh, cth, str(90 - elev)]

    # Run the string and get the output
    output = subprocess.Popen(monoStr, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
    
    if debug is True:
        print output
    # Try to parse out the brightness temperatures from the MonoRTM output
    try:
        output = output.split('ODliq')[1].strip().split()
    except:
        # Means the MonoRTM didn't run properly
        print "ERROR with MonoRTM", output
        sys.exit()

    # The MonoRTM ran successfully, parse out the brightness temperatures
    len_out = len(output)
    output = np.asarray(output, dtype=np.float64)
    output = np.reshape(output, (len_out/7, 7))
    monoRTM_output = output[:,1] # The brightness temperatures

    return monoRTM_output

date = sys.argv[1] # YYYYMMDD
hour = sys.argv[2] # HH

path = '/raid/FRDD/Dave.Turner/data/norman/sonde/netcdf/OUNsondeX1.a1.' + date + "." + hour + '0000.cdf'
print "Running MonoRTM..."
print monoRTM(path)
print
print "Making LBLRTM TP5..."
print LBLRTM(path)

