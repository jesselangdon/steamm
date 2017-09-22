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
# Last Updated: 08/31/2016
# Copyright:   (c) South Fork Research, Inc. 2016
# Licence:      FreeBSD License
# Version:      0.2
#-------------------------------------------------------------------------------

# Import modules
import os
import shutil
import gdal
import gdalconst
import get_modis as gm

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

# Functions for creating and managing directories for the MODIS pre-processing tool

def dir_list(data_dir, data_product, list_year):
    """Create a list of full directory paths for downloaded MODIS files."""
    dir_list= []
    for d in data_product:
        for y in list_year:
            dir_list.append("{}\{}\{}".format(data_dir, d, y))
    return dir_list


def create_dir(dir_list):
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

def download_hdf(platform, product_list, year_list, tile_list, doy_start, doy_end, data_dir, username, password, proxy=None):
    """download HDF files for multiple years, using get_modis."""
    for product in product_list:
        for year in year_list:
            for tile in tile_list:
                dir_hdf = """{}\{}\{}""".format(data_dir, product, year)
                gm.get_modisfiles(platform, product, year, tile, proxy, username, password, doy_start, doy_end, dir_hdf )
            message = 'All HDF files downloaded for %d.' % (year)
            print message
    return


def get_hdf_filepaths(hdf_dir):
    """Get a list of HDF files downloaded by get_modis.py, which is be used for iterating through hdf file conversion."""
    print "Building list of downloaded HDF files..."
    hdf_file_list = []
    hdf_filepath_list = []
    for dir in hdf_dir:
        for dir_path, subdir, files in os.walk(dir):
            for f in files:
                if f.endswith(".hdf"):
                    hdf_file_list.append(os.path.splitext(f)[0])
                    hdf_filepath_list.append(os.path.join(dir_path, f))
    return hdf_filepath_list, hdf_file_list


def build_file_array(hdf_file_list):
    """Split HDF file names into array, allowing other functions to access the julian date values."""
    print "Creating array based on HDF file names..."
    hdf_file_array = []
    for f in hdf_file_list:
        hdf_file_array.append(f.split("."))
    return hdf_file_array


def get_file_dates(hdf_file_array):
    """Build list of collection dates from an HDF file array."""
    print "Building list of MODIS HDF file collection dates..."
    hdf_date_list = []
    for f in hdf_file_array:
        hdf_date_list.append(f[1])
    return hdf_date_list


def find_dup_file_dates(hdf_date_list, swath_id):
    """Extracts list of unique days from list of all file dates."""
    print "Extracting list of non-duplicate MODIS HDF collection dates..."
    if len(swath_id) > 1:
        hdf_dates = set([d for d in hdf_date_list if hdf_date_list.count(d)>1])
    else:
        hdf_dates = hdf_date_list
    sorted_dates = sorted(hdf_dates)
    return sorted_dates


def get_modis_wkt(steamm_script):
    """Returns the filepath to the MODIS Sin WKT projection file"""
    print "Finding the file path to the MODIS WKT projection file..."
    steamm_path = os.path.abspath(steamm_script)
    steamm_dir = os.path.dirname(steamm_path)
    modis_wkt_filepath = os.path.join(steamm_dir, "MODIS_sin.wkt")
    return modis_wkt_filepath


def convert_hdf(input_dir, dir_list, hdf_filepath_list, hdf_file_list):
    global src_xres
    global src_yres
    """Converts MODIS HDF files to a geotiff format."""
    print "Converting MODIS HDF files to geotiff format..."
    out_format = 'GTiff'
    local_array = zip(hdf_filepath_list, hdf_file_list)
    out_geotiff_list = []

    for dir in dir_list:
        for in_filepath, out_filename in local_array:

            # Open the LST_Day_1km dataset
            src_open = gdal.Open(in_filepath, gdalconst.GA_ReadOnly) # open filewith all sub-datasets
            src_subdatasets = src_open.GetSubDatasets() # make a list of sub-datasets in the HDF file
            subdataset = gdal.Open(src_subdatasets[0][0])

            # Get parameters from LST dataset
            src_cols = subdataset.RasterXSize
            src_rows = subdataset.RasterYSize
            src_band_count = subdataset.RasterCount
            src_geotransform = subdataset.GetGeoTransform()
            src_xres = src_geotransform[1]
            src_yres = src_geotransform[5]
            src_proj = subdataset.GetProjection()

            # Read dataset to array
            src_band = subdataset.GetRasterBand(1)
            src_array = src_band.ReadAsArray(0, 0, src_cols, src_rows)

            # Set up output file
            driver = gdal.GetDriverByName(out_format)
            out_file = "%s\%s.%s" % (dir, out_filename, "tif")
            out_geotiff = driver.Create(out_file, src_cols, src_rows, src_band_count, gdal.GDT_Float32)
            out_geotiff.SetGeoTransform(src_geotransform)
            out_geotiff.SetProjection(src_proj)
            out_geotiff.GetRasterBand(1).WriteArray(src_array)
            out_geotiff.FlushCache()

            # Create list of output geotiffs
            out_geotiff_list.append(out_file)

    return out_geotiff_list, src_xres, src_yres


# main function to download and convert HDFs to tiff
def main(proj_dir, data_product, process_yr_str, swath_id, geo_rca, doy_start_str, doy_end_str, username, password, platform = 'MOLT'):

    # Temporary variable conversion
    doy_start = int(doy_start_str)
    doy_end = int(doy_end_str)

    # Create download directories and download from HDF files from USGS server
    #dir_hdf = '%s\\%s\\%s\\%s' % (proj_dir, dir_list[0], source_subdir_list[0], process_yr[0])
    dirs = dir_list(proj_dir, data_product, process_yr)
    create_dir(dirs)
    download_hdf(platform, data_product, process_yr, swath_id, doy_start, doy_end, data_dir, username, password)

    hdf_filepath_list, hdf_file_list = get_hdf_filepaths(dirs)
    hdf_file_array = build_file_array(hdf_file_list)
    hdf_date_list = get_file_dates(hdf_file_array)
    hdf_dates = find_dup_file_dates(hdf_date_list, swath_id)

    # File conversion
    geotiff_list, xres, yres = convert_hdf(proj_dir, dirs, hdf_filepath_list, hdf_file_list)


# testing variables
data_dir = r'C:\JL\Testing\STeAMM\test20160912'
data_product = ['MOD11A2.005']
process_yr = [2015]
swath_id = ['h08v05']
geo_rca = r'C:\dev\steamm_working\testing\BNG_outline.shp'
doy_start_str = 1
doy_end_str = 9
username = 'jesselangdon'
password = 'Jw-3i1970'

# call the main function, run the program
if __name__ == '__main__':
    main(data_dir, data_product, process_yr, swath_id, geo_rca, doy_start_str, doy_end_str, username, password)