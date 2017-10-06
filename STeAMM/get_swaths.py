#-------------------------------------------------------------------------------
# Name:         preprocess.py
#
# Summary:      The modis_preprocess module allows the user to download MODIS LST datasets
#               as HDF files to the user's local computer.  The HDF files are then automatically
#               converted from HDF to geotiff format.
#
# Project:      Stream Temperature Automated Modeler using MODIS (STeAMM)
#
# Author:       Jesse Langdon
#
# References:   McNyset, Kristina M., Carol J. Volk, and Chris E. Jordan. "Developing
#               an Effective Model for Predicting Spatially and Temporally Continuous
#               Stream Temperatures from Remotely Sensed Land Surface Temperatures."
#               Water 7.12 (2015): 6827-6846.
#
# Last Updated: 10/04/2017
# Copyright:    (c) South Fork Research, Inc. 2017
# Licence:      FreeBSD License
# Version:      0.3
#-------------------------------------------------------------------------------

# Import modules
import os
import sys
import shutil
# import gdal
# import gdalconst

tool_dir = os.path.normpath(os.path.dirname(__file__))
sys.path.insert(0, tool_dir + '\externals\get_modis' )
for path in sys.path:
    print path
import get_modis as gm

# TODO remove CLI example text block
'''
# ---------------
# Input variables

# New data directory filepath and name
data_dir =

# Select a MODIS Data Product by using the product ID (i.e. MOD11A1.005) -')
# MOD11A1.005 = Land Surface Temperature/Emissivity Daily L3 Global 1km')
# MOD11A2.005 = Land Surface Temperature/Emissivity 8-Day L3 Global 1km')
data_product =

# Year to be processed (i.e. 2015)
process_yr_str =

# MODIS Swath IDs to process (multiple tiles: h09v04,h10v04)
swath_id_raw =
swath_id = swath_id_raw.split(',')

# Beginning and end dates, in julian day format (i.e. 1, 365)
doy_start_str =    #  Beginning of year
doy_end_str =     # End of year

username = jesselangdon
password = Jw-3i1970
'''

#CONSTANTS
PLATFORM = 'MOLT' # L
#MODIS_PRODUCTS = {'Daily':'MOD11A1.005', '8-day':'MOD11A2.005'}
MODIS_PRODUCTS = {'Daily':'MOD11A1.005'}

def build_dir_list(project_dir, year_list, product_list):
    """Create a list of full directory paths for downloaded MODIS files."""
    dir_list = []
    for product in product_list:
        for year in year_list:
            dir_list.append("{}\{}\{}".format(project_dir, product, year))
    return dir_list


def make_dirs(dir_list):
    """Creates new directories to store downloaded MODIS files"""
    for dir in dir_list:
        if not os.path.exists(dir):
            print ("Creating new directory " + dir)
            os.makedirs(dir, 0777)
        else:
            print ("Overwriting existing directory with " + dir)
            shutil.rmtree(dir)
            os.makedirs(dir, 0777)
    return


def download_hdf(product_list, year_list, swath_list, doy_start, doy_end, project_dir, username, password, proxy=None):
    """download HDF files for multiple years, using get_modis."""

    for product in product_list.itervalues():
        for year in year_list:
            for swath in swath_list:
                hdf_dir = """{}\{}\{}""".format(project_dir, year, product)
                gm.get_modisfiles(username, password, PLATFORM, product, year, swath, proxy, doy_start, doy_end)
            message = 'All HDF files downloaded for %d.' % (year)
            print message
    return hdf_dir


def get_hdf_filepaths(hdf_dir):
    """Get a list of downloaded HDF files which is be used for iterating through hdf file conversion."""
    print "Building list of downloaded HDF files..."
    hdf_filename_list = []
    hdf_filepath_list = []
    for dir in hdf_dir:
        for dir_path, subdir, files in os.walk(dir):
            for f in files:
                if f.endswith(".hdf"):
                    hdf_filename_list.append(os.path.splitext(f)[0])
                    hdf_filepath_list.append(os.path.join(dir_path, f))
    return hdf_filename_list, hdf_filepath_list


def build_file_array(hdf_filename_list):
    """Split HDF file names into array, so other functions to access the julian date values."""
    print "Creating array based on HDF file names..."
    hdf_file_array = []
    for f in hdf_filename_list:
        hdf_file_array.append(f.split("."))
    return hdf_file_array


def get_file_dates(hdf_file_array):
    """Build list of collection dates from an HDF file array."""
    print "Building list of MODIS HDF file collection dates..."
    hdf_date_list = []
    for f in hdf_file_array:
        hdf_date_list.append(f[1])
    return hdf_date_list


def find_dup_file_dates(hdf_date_list, swath_list):
    """Extracts list of unique days from list of all file dates."""
    print "Extracting list of non-duplicate MODIS HDF collection dates..."
    if len(swath_list) > 1:
        hdf_dates = set([d for d in hdf_date_list if hdf_date_list.count(d)>1])
    else:
        hdf_dates = hdf_date_list
    sorted_dates = sorted(hdf_dates)
    return sorted_dates


# main function, to serve as example
def main(proj_dir,
         data_products,
         process_yr_str,
         swath_id,
         doy_start_str,
         doy_end_str,
         username,
         password):

    # Create download directories and download from HDF files from USGS server
    dirs = build_dir_list(proj_dir, data_products, process_yr)
    make_dirs(dirs)
    download_hdf(MODIS_PRODUCTS, process_yr, swath_id, doy_start, doy_end, data_dir, username, password)

    hdf_filepath_list, hdf_file_list = get_hdf_filepaths(dirs)
    hdf_file_array = build_file_array(hdf_file_list)
    hdf_date_list = get_file_dates(hdf_file_array)
    hdf_dates = find_dup_file_dates(hdf_date_list, swath_id)


# testing variables
data_dir = r'C:\JL\Testing\STeAMM\test20160912'
process_yr = [2015, 2016]
swath_id = ['h09v04', 'h10v04']
doy_start = 1
doy_end = 9
username = 'jesselangdon'
password = 'Jw-3i1970'

# call the main function, run the program
if __name__ == '__main__':
    main(data_dir,
         MODIS_PRODUCTS,
         process_yr,
         swath_id,
         doy_start,
         doy_end,
         username, password)