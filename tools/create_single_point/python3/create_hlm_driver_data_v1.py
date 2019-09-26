#! /usr/bin/env python3.7
# on mac need to install libs as: python3 -m pip install xarray
# helpful: https://towardsdatascience.com/handling-netcdf-files-using-xarray-for-absolute-beginners-111a8ab4463f
# helpful: https://rabernat.github.io/research_computing_2018/xarray.html
#
#  Import libraries
import sys
import os
from os.path import expanduser,basename
from getpass import getuser
import string
import subprocess
import numpy as np
import xarray as xr

def mprint(mstr):
    vnum=sys.version_info[0]
    if vnum == 3:
        print(mstr)
    if vnum == 2:
        print(mstr)
        
myname=getuser()
pwd=os.getcwd()
mprint(myname)
mprint(pwd)

'''
#------------------------------------------------------------------#
#---------------------  Instructions  -----------------------------#
#------------------------------------------------------------------#
After creating a case using a global compset, run preview_namelist.  
From the resulting lnd_in file in the run directory, find the name 
of the domain file, and the surface data file.  
From the datm streams files (e.g. datm.streams.txt.CLMGSWP3v1.Precip)
find the name of the datm forcing data domain file and forcing files.  
Use these file names as the sources for the single point files to 
be created (see below).

After running this script, point to the new CLM domain and surface 
dataset using the user_nl_clm file in the case directory.  In addition, 
copy the datm.streams files to the case directory, with the prefix 
'user_', e.g. user_datm.streams.txt.CLMGSWP3v1.Precip.  Change the 
information in the user_datm.streams* files to point to the single 
point datm data (domain and forcing files) created using this script.  

The domain file is not set via user_nl_clm, but requires changing 
LND_DOMAIN and ATM_DOMAIN (and their paths) in env_run.xml.  

Using single point forcing data requires specifying the nearest 
neighbor mapping algorithm for the datm streams (usually they are 
the first three in the list) in user_nl_datm: mapalgo = 'nn','nn','nn', 
..., where the '...' can still be 'bilinear', etc, depending on the 
other streams that are being used, e.g. aerosols, anomaly forcing, 
bias correction.

The file env_mach_pes.xml should be modified to specify a single 
processor.  The mpi-serial libraries should also be used, and can be 
set in env_build.xml by changing "MPILIB" to "mpi-serial" prior to 
setting up the case.  

The case for the single point simulation should have river routing 
and land ice models turned off (i.e. the compset should use stub 
models SROF and SGLC)
'''

# TODO
# need to switch all path to os.path.join() because it can handle different OS platforms, e.g. Win vs Mac vs Linux
# Make it easy for user-selectable domain/surf files

#####  Set control flags

#--  Specify point to extract
plon = 270.6523
plat = 46.2420

#--  Create regional CLM domain file
create_domain   = True
#--  Create CLM surface data file
create_surfdata = True
#--  Create CLM surface data file - doesnt work yet
create_landuse  = False
#--  Create single point DATM atmospheric forcing data
create_datm     = True
#-- What years to generate drivers for?
datm_syr=1980
datm_eyr=2010
#datm_eyr=1981

#-- what met driver?
met_driver = 'atm_forcing.datm7.GSWP3.0.5d.v1.c170516'

#--  Modify landunit structure
overwrite_single_pft = True
dominant_pft         = 1 #1 NE Temp Tree 7 BDF
zero_nonveg_pfts     = True
uniform_snowpack     = False
no_saturation_excess = False

#--  Specify input and output directories
cesm_input_datasets = '/Volumes/data/Model_Data/cesm_input_datasets/'
dir_output = 'Data/cesm_input_data/single_point/'
site_name = 'US-Syv'
home = expanduser('~')
# need to redo this part and not re-use dir_output
dir_output = os.path.join(home,dir_output,site_name)
os.makedirs(os.path.dirname(dir_output), exist_ok=True)

# -- input datm
dir_input_datm = os.path.join(cesm_input_datasets,'atm/datm7/',met_driver)
dir_output_datm = os.path.join(dir_output,'datmdata',met_driver)
os.makedirs(dir_output_datm, exist_ok=True)

#--  Set input and output filenames
tag=str(plon)+'_'+str(plat)

#--  Set time stamp
command='date "+%y%m%d"'
x2=subprocess.Popen(command,stdout=subprocess.PIPE,shell='True')
x=x2.communicate()
timetag = x[0].strip()

#--  Specify land domain file  ---------------------------------
fdomain  = os.path.join(cesm_input_datasets,'share/domains/domain.lnd.fv0.9x1.25_gx1v6.090309.nc')
fdomain2 = os.path.join(dir_output, os.path.splitext(basename(fdomain))[0]+'_'+site_name+'.nc')
#fdomain  = '/Volumes/data/Model_Data/cesm_input_datasets/share/domains/domain.lnd.fv0.9x1.25_gx1v6.090309.nc'
#fdomain2 = dir_output + 'domain.lnd.fv0.9x2.5_gx1v6.'+tag+'_090309.nc'

#--  Specify surface data file  --------------------------------
#fsurf    = '/Users/shawnserbin/Data/cesm_input_data/lnd/clm2/surfdata_map/surfdata_0.9x2.5_78pfts_CMIP6_simyr2000_c170824.nc'
fsurf = os.path.join(cesm_input_datasets,'lnd/clm2/surfdata_map/surfdata_0.9x1.25_78pfts_CMIP6_simyr2000_c170824.nc')
#fsurf2   = dir_output + 'surfdata_0.9x1.25_16pfts_CMIP6_simyr2000_'+tag+'.c170706.nc'
#fsurf2 = dir_output + '/surfdata_0.9x1.25_78pfts_CMIP6_simyr2000_'+tag+'_c170824.nc'
fsurf2 = os.path.join(dir_output,os.path.splitext(basename(fsurf))[0]+'_'+site_name+'.nc')

#--  Specify landuse file  -------------------------------------
fluse    = '/glade/p/cesmdata/cseg/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1.9x2.5_hist_78pfts_CMIP6_simyr1850-2015_c170824.nc'
fluse2   = dir_output + 'landuse.timeseries_1.9x2.5_hist_78pfts_CMIP6_simyr1850-2015_'+tag+'.c170824.nc'

#--  Specify datm domain file  ---------------------------------
#fdatmdomain = '/Users/shawnserbin/Data/cesm_input_data/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v1.c170516/domain.lnd.360x720_gswp3.0v1.c170606.nc'
fdatmdomain = os.path.join(dir_input_datm,'domain.lnd.360x720_gswp3.0v1.c170606.nc')
#fdatmdomain2  = dir_output_datm + '/domain.lnd.360x720_gswp3.0v1.'+tag+'_c170606.nc'
#fdatmdomain2  = os.path.join(dir_output, os.path.splitext(basename(fdatmdomain))[0]+'_'+site_name+'.nc')
fdatmdomain2  = os.path.join(dir_output_datm, basename(fdatmdomain))


#--  Create CTSM domain file
if create_domain:
    f1  = xr.open_dataset(fdomain)
    lon0 = np.asarray(f1['xc'][0,:])
    lat0 = np.asarray(f1['yc'][:,0])
    lon = xr.DataArray(lon0,name='lon',dims='ni',coords={'ni':lon0})
    lat = xr.DataArray(lat0,name='lat',dims='nj',coords={'nj':lat0})
    f2 = f1.assign({'lon':lon,'lat':lat})
    f2 = f2.reset_coords(['xc','yc'])

    # extract gridcell closest to plon/plat
    f3 = f2.sel(ni=plon,nj=plat,method='nearest')

    # expand dimensions
    f3 = f3.expand_dims(['nj','ni'])

    # mode 'w' overwrites file
    print('**** Write domain file to output directory')
    f3.to_netcdf(path=fdomain2, mode='w')
    mprint('created file '+fdomain2)
    f1.close(); f2.close(); f3.close()

#--  Create CTSM surface data file
if create_surfdata:
    #f1  = xr.open_dataset(fsurf, cache=True)
    mprint('**** Open '+fsurf)
    f1  = xr.load_dataset(fsurf)
    # create 1d variables
    lon0=np.asarray(f1['LONGXY'][0,:])
    lon=xr.DataArray(lon0,name='lon',dims='lsmlon',coords={'lsmlon':lon0})
    lat0=np.asarray(f1['LATIXY'][:,0])
    lat=xr.DataArray(lat0,name='lat',dims='lsmlat',coords={'lsmlat':lat0})
    f2=f1.assign({'lon':lon,'lat':lat})
    # extract gridcell closest to plon/plat
    f3 = f2.sel(lsmlon=plon,lsmlat=plat,method='nearest')
    # expand dimensions
    f3 = f3.expand_dims(['lsmlat','lsmlon'])
 
    # modify surface data properties
    if overwrite_single_pft:
        atemp = f3.PCT_NAT_PFT.attrs
        f3['PCT_NAT_PFT'] = xr.where(f3['PCT_NAT_PFT']>0, 0, 0)
        f3.PCT_NAT_PFT.attrs = atemp
        f3['PCT_NAT_PFT'][:,:,dominant_pft] = 100
        # for debugging - to check modification is working properly
        #mprint(f3)
        #mprint(f3['PCT_NAT_PFT'][:,:,dominant_pft])
        mprint(f3['PCT_NAT_PFT'])
        del atemp
    if zero_nonveg_pfts:
        #f3.PCT_NATVEG.values = np.array([[100]])
        f3.PCT_NATVEG.data = np.array([[100]])
        #f3['PCT_CROP'][:,:]    = 0
        f3.PCT_CROP.data = np.array([[0]])
        #f3['PCT_LAKE'][:,:]    = 0.
        f3.PCT_LAKE.data = np.array([[0.]])
        #f3['PCT_WETLAND'][:,:] = 0.
        f3.PCT_WETLAND.data = np.array([[0.]])
        #f3['PCT_URBAN'][:,:,]   = 0.
        atemp = f3.PCT_URBAN.attrs
        f3['PCT_URBAN'] = xr.where(f3['PCT_URBAN']>0, 0, 0)
        f3.PCT_URBAN.attrs = atemp
        #f3['PCT_GLACIER'][:,:] = 0.
        f3.PCT_GLACIER.data = np.array([[0.]])
        del atemp
    if uniform_snowpack:
        #f3['STD_ELEV'][:,:] = 20.
        f3.STD_ELEV.data = np.array([[20.]])
    if no_saturation_excess:
        #f3['FMAX'][:,:] = 0.
        f3.FMAX.data = np.array([[0.]])

    # specify dimension order 
    #f3 = f3.transpose(u'time', u'cft', u'natpft', u'lsmlat', u'lsmlon')
    f3 = f3.transpose('time', 'cft', 'lsmpft', 'natpft', 'nglcec', 'nglcecp1', 'nlevsoi', 'nlevurb', 'numrad', 'numurbl', 'lsmlat', 'lsmlon')
    # mode 'w' overwrites file
    print('**** Write surfdata file to output directory')
    f3.to_netcdf(path=fsurf2, mode='w')
    mprint('created file '+fsurf2)
    f1.close(); f2.close(); f3.close()

    ''' this is buggy; can't re-write a file within the same session
    # modify new surface data file
    if overwrite_single_pft:
        f1  = xr.open_dataset(fsurf2)
        f1['PCT_NAT_PFT'][:,:,:] = 0
        f1['PCT_NAT_PFT'][:,:,dominant_pft] = 100
        f1.to_netcdf(path='~/junk.nc', mode='w')
        #f1.to_netcdf(path=fsurf2, mode='w')
        f1.close()
    if zero_nonveg_pfts:
        #f1  = xr.open_dataset(fsurf2)
        f1  = xr.open_dataset('~/junk.nc')
        f1['PCT_NATVEG']  = 100
        f1['PCT_CROP']    = 0
        f1['PCT_LAKE']    = 0.
        f1['PCT_WETLAND'] = 0.
        f1['PCT_URBAN']   = 0.
        f1['PCT_GLACIER'] = 0.
        #f1.to_netcdf(path=fsurf2, mode='w')
        f1.to_netcdf(path='~/junk2.nc', mode='w')
        f1.close()
    '''


#--  Create CTSM transient landuse data file
if create_landuse:
    f1  = xr.open_dataset(fluse)
    # create 1d variables
    lon0=np.asarray(f1['LONGXY'][0,:])
    lon=xr.DataArray(lon0,name='lon',dims='lsmlon',coords={'lsmlon':lon0})
    lat0=np.asarray(f1['LATIXY'][:,0])
    lat=xr.DataArray(lat0,name='lat',dims='lsmlat',coords={'lsmlat':lat0})
    f2=f1.assign({'lon':lon,'lat':lat})
    #f2=f1.assign()
    #f2['lon'] = lon
    #f2['lat'] = lat
    # extract gridcell closest to plon/plat
    f3 = f2.sel(lsmlon=plon,lsmlat=plat,method='nearest')

    # expand dimensions
    f3 = f3.expand_dims(['lsmlat','lsmlon'])
    # specify dimension order 
    #f3 = f3.transpose('time','lat','lon')
    f3 = f3.transpose('time', 'cft', 'natpft', 'lsmlat', 'lsmlon')
    #f3['YEAR'] = f3['YEAR'].squeeze()

    # revert expand dimensions of YEAR
    year = np.squeeze(np.asarray(f3['YEAR']))
    x = xr.DataArray(year, coords={'time':f3['time']}, dims='time', name='YEAR')
    x.attrs['units']='unitless'
    x.attrs['long_name']='Year of PFT data'
    f3['YEAR'] = x
    #print(x)
    #mprint(f3)
    #stop
    # mode 'w' overwrites file
    f3.to_netcdf(path=fluse2, mode='w')
    mprint('created file '+fluse2)
    f1.close(); f2.close(); f3.close()

#--  Create single point atmospheric forcing data
if create_datm:
    #--  create datm domain file
    f1  = xr.open_dataset(fdatmdomain)
    # create 1d coordinate variables to enable sel() method
    lon0=np.asarray(f1['xc'][0,:])
    lat0=np.asarray(f1['yc'][:,0])
    lon=xr.DataArray(lon0,name='lon',dims='ni',coords={'ni':lon0})
    lat=xr.DataArray(lat0,name='lat',dims='nj',coords={'nj':lat0})

    f2=f1.assign({'lon':lon,'lat':lat})
    f2 = f2.reset_coords(['xc','yc'])

    # extract gridcell closest to plon/plat
    f3 = f2.sel(ni=plon,nj=plat,method='nearest')
    # expand dimensions
    f3 = f3.expand_dims(['nj','ni'])

    # mode 'w' overwrites file
    print('**** Write domain.lnd file to output directory')
    f3.to_netcdf(path=fdatmdomain2, mode='w')
    mprint('created file '+fdatmdomain2)
    f1.close(); f2.close(); f3.close()

    #--  specify subdirectory names and filename prefixes
    solrdir = 'Solar'
    precdir = 'Precip'
    tpqwldir = 'TPHWL'
    # !!! these should be found automatically. Replace this with a command to find the common filenames !!!
    prectag = 'clmforc.GSWP3.c2011.0.5x0.5.Prec.'
    solrtag = 'clmforc.GSWP3.c2011.0.5x0.5.Solr.'
    tpqwtag = 'clmforc.GSWP3.c2011.0.5x0.5.TPQWL.'

    #--  create data files  
    infile=[]
    outfile=[]
    for y in range(datm_syr,datm_eyr+1):
      ystr=str(y)
      for m in range(1,13):
         mstr=str(m) 
         if m < 10:
            mstr='0'+mstr

         dtag=ystr+'-'+mstr

         # setup inputs and create outputs - removed insertion of lat/long into filename to make it easier to use with CLM 
         #fsolar=dir_input_datm+solrdir+solrtag+dtag+'.nc'
         fsolar = os.path.join(dir_input_datm, solrdir, solrtag+dtag+'.nc')
         #fsolar2=dir_output_datm+solrtag+tag+'.'+dtag+'.nc'
         fsolar2 = os.path.join(dir_output_datm,solrdir,solrtag+dtag+'.nc')
         os.makedirs(os.path.dirname(fsolar2), exist_ok=True)
         #fprecip=dir_input_datm+precdir+prectag+dtag+'.nc'
         fprecip = os.path.join(dir_input_datm, precdir, prectag+dtag+'.nc')
         #fprecip2=dir_output_datm+prectag+tag+'.'+dtag+'.nc'
         fprecip2 = os.path.join(dir_output_datm,precdir,prectag+dtag+'.nc')
         os.makedirs(os.path.dirname(fprecip2), exist_ok=True)
         #ftpqw=dir_input_datm+tpqwldir+tpqwtag+dtag+'.nc'
         ftpqw = os.path.join(dir_input_datm, tpqwldir, tpqwtag+dtag+'.nc')
         #ftpqw2=dir_output_datm+tpqwtag+tag+'.'+dtag+'.nc'
         ftpqw2 = os.path.join(dir_output_datm,tpqwldir,tpqwtag+dtag+'.nc')
         os.makedirs(os.path.dirname(ftpqw2), exist_ok=True)

         infile+=[fsolar,fprecip,ftpqw]
         outfile+=[fsolar2,fprecip2,ftpqw2]

    nm=len(infile)
    for n in range(nm):
        mprint(outfile[n]+'\n')
        file_in = infile[n]
        file_out = outfile[n]
    
        f1  = xr.open_dataset(file_in)
        # create 1d coordinate variables to enable sel() method
        lon0=np.asarray(f1['LONGXY'][0,:])
        lat0=np.asarray(f1['LATIXY'][:,0])
        lon=xr.DataArray(lon0,name='lon',dims='lon',coords={'lon':lon0})
        lat=xr.DataArray(lat0,name='lat',dims='lat',coords={'lat':lat0})
        #f2=f1.assign({'lon':lon,'lat':lat})
        f2=f1.assign()
        f2['lon'] = lon
        f2['lat'] = lat
        f2.reset_coords(['LONGXY','LATIXY'])
        # extract gridcell closest to plon/plat
        f3  = f2.sel(lon=plon,lat=plat,method='nearest')
        # expand dimensions
        f3 = f3.expand_dims(['lat','lon'])
        # specify dimension order 
        f3 = f3.transpose('scalar','time','lat','lon')

        # mode 'w' overwrites file
        print('**** Write drivers files to datmdata output directory')
        f3.to_netcdf(path=file_out, mode='w')
        f1.close(); f2.close(); f3.close()

      
    mprint('datm files written to: '+dir_output_datm)