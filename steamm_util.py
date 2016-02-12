#-------------------------------------------------------------------------------------
# Name:         steamm_util.py
#
# Summary:      STeAMM (Stream Temperature Automated Modeler using MODIS) is a QGIS
#               Plugin that automates the process of modeling stream temperature using
#               the methodology described in McNyset, et al. 2015. STeAMM is written
#               in Python, and relies on several external libraries, including gdal,
#               numpy, matplotlib, and PyQT.  Specifically this file includes classes,
#               methods, and functions that are used by the main function in steamm.py
#               and the main.ui PyQT form.
#
# Author:       Jesse Langdon
#
# References:   McNyset, Kristina M., Carol J. Volk, and Chris E. Jordan. "Developing
#               an Effective Model for Predicting Spatially and Temporally Continuous
#               Stream Temperatures from Remotely Sensed Land Surface Temperatures."
#               Water 7.12 (2015): 6827-6846.
#
# Last Updated: 02/12/2016
#
# Copyright:    (c) South Fork Research, Inc. 2016
#
# Licence:      FreeBSD License
#-------------------------------------------------------------------------------------


## import modules
import os.path
import get_modis as gm


# ----------------------
# class projectDir
# create a list with project directories
def create_dir_lists():
    dir_list = ["1source_data", "2temp_files", "3model_output"]
    source_subdir_list = ["1modis_hdf", "2vector_inputs"]
    products_subdir_list = ["1crb_extent", "2polygons", "3stream_network"]
    return dir_list, source_subdir_list, products_subdir_list


# create list of full paths to all project directories
def create_full_dir_list(input_dir, dir_list, source_subdir_list, products_subdir_list):
    full_dir_list = []
    for d in dir_list:
        full_dir_list.append(input_dir + "\\" + d)
    # create sub-directories for 1source_data folder
    for s in source_subdir_list:
        full_dir_list.append(input_dir + "\\" + dir_list[0] + "\\" + s)
    # create sub-directories for 3products folder
    for p in products_subdir_list:
        full_dir_list.append(input_dir + "\\" + dir_list[2] + "\\" + p)
    return full_dir_list


# create new project directory using STeAMM project directory schema
def create_new_dir(input_dir, dir_list, source_subdir_list, products_subdir_list):
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        # create top level directories
        for d in dir_list:
            os.makedirs(os.path.join(input_dir, d))
        # create sub-directories for 1source_data folder
        for s in source_subdir_list:
            dir_1source = input_dir + "\\" + dir_list[0]
            os.makedirs(os.path.join(dir_1source, s))
        # create sub-directories for 3products folder
        for p in products_subdir_list:
            dir_3products = input_dir + "\\" + dir_list[2]
            os.makedirs(os.path.join(dir_3products, p))
    else:
        print "WARNING: The directory already exists"
    return


# if "existing project" is selected in main form, check if directory with STeAMM schema exists
def check_dir_schema(input_dir, full_dir_list):
    user_dir_list = []
    missing_dir_list = []
    for user_root, user_dir, user_files in os.\
            walk(input_dir):
        for d in user_dir:
            user_dir_list.append(os.path.join(user_root, d))
    for ideal_dir in full_dir_list:
        if ideal_dir not in user_dir_list:
            missing_dir_list.append(ideal_dir)
    if len(missing_dir_list ) >= 1:
        message = "Missing directories: %s" % (str(missing_dir_list))
    else:
        message = "All required directories are present."
    return message


# add folder to .\1source_data for each selected year
def create_year_folders(year_list, input_dir, dir_list, source_subdir_list):
    subdir_hdf = input_dir + "\\" + dir_list[0] + "\\" + source_subdir_list[0]
    for y in year_list:
        os.makedirs(os.path.join(subdir_hdf, str(y)))
    return subdir_hdf


# download HDF files for multiple years, using get_modis
def download_hdf(platform, product, year_list, tile_list, doy_start, doy_end, dir_hdf):
    for year in year_list:
        for tile in tile_list:
            dir_year = dir_hdf + "\\" +  str(year)
            gm.get_modisfiles(platform, product, year, tile, proxy, doy_start, doy_end, dir_year)
    return


# --------------------
# class buildHDFtables
# get list of downloaded files downloaded by get_modis.py
### this will be used for iterating through hdf file conversion
def get_hdf_filepaths(hdf_dir):
    import os.path
    hdf_filepath_list = []
    for dir_path, subdir, files in os.walk(hdf_dir):
        for f in files:
            if f.endswith(".hdf"):
                hdf_filepath_list.append(os.path.join(dir_path, f))
    return hdf_filepath_list

# split hdf file names into array
### this will allow other functions to access the julian date numbers
def get_hdf_file_array(hdf_filepath_list):
    hdf_file_array = []
    for h in hdf_filepath_list:
        hdf_file_array.append(h.split("."))
    return hdf_file_array

# create list of HDF file names without extension
### will be used to assign names to output files (i.e. geotiffs)
def get_hdf_filenames(hdf_file_array):
        # ---
    return hdf_filename_list

# build array of HDF files that were captured on same day
### this will iterate through the hdf_filename_array, find all matching dates
### then pull the associated hdf filenames into a list record in new array
### This new list can then be used by the mosaic function.
def find_hdf_same_day(hdf_file_array, hdf_filepath_list):
        # ---
    return hdf_sameday_list

# class convertLST
# convert HDF file to ascii file format (or Numpy array?)
### Out will be used for the missing value interpolation of daily values
def hdf_to_ascii(hdf_list):
    # ---
    return hdf_ascii_list

# interpolate missing LST values
### this is currently accomplished using Kris's R code. May need to be ported from Numpy
def interpolate_lst(  ):
    # --
    return intrp_lst_list

# convert HDF file to geotiff
### this could also be accomplished by simply using os.system to call the gdal_translate utility
def convert_hdf(hdf_list):
    import gdal
    import gdalconst
    out_format = 'GTiff'
    ### TESTING ###
    out_file = r'C:\repo\steamm\testing\_2GTiff\test_output.tif' #this should go to dir_3products
    ### TESTING ###
    for hdf_file in hdf_list:

        #Open the LST_Day_1km dataset
        src_open = gdal.Open(hdf_file, gdalconst.GA_ReadOnly) # open the HDF file with all sub-datasets
        src_subdatasets = src_open.GetSubDatasets() # make a list of sub-datasets in the HDF file
        subdataset = gdal.Open(src_subdatasets[0][0])

        #Get parameters from LST dataset
        src_cols = subdataset.RasterXSize
        src_rows = subdataset.RasterYSize
        src_band_count = subdataset.RasterCount
        src_geotransform = subdataset.GetGeoTransform()
        src_proj = subdataset.GetProjection()

        #Read dataset to array
        src_band = subdataset.GetRasterBand(1)
        src_array = src_band.ReadAsArray(0, 0, src_cols, src_rows)

        #Set up output file
        driver = gdal.GetDriverByName(out_format)
        out_geotiff = driver.Create(out_file, src_cols, src_rows, src_band_count, gdal.GDT_Float32)
        out_geotiff.SetGeoTransform(src_geotransform)
        out_geotiff.SetProjection(src_proj)
        out_geotiff.GetRasterBand(1).WriteArray(src_array)
        out_geotiff.FlushCache()
    return out_geotiff, out_geotiff.GetRasterBand(1)

# need to figure out how to mosaic LST rasters that were collected on same day by MODIS
### will most likely use the first 6 or 8 digits of the date embedded in the HDF file name (i.e. 20140120)
def mosaic_vrt(hdf_filename_list, dir_vrt, dir_input, wkt):
    # declare local variables
    file_ext = 'tif'
    in_rasters = dir_input + r"\*." + file_ext
    out_mosaic_list = []
    # iterate through list of filenames, create mosaic
    for f in list_filenames:
        out_mosaic = dir_vrt + r"\\" + f + r"_mosaic.vrt"
        expr = 'gdalbuildvrt -a_srs %s %s %s' % (wkt, out_vrt, in_rasters)
        os.system(expr)
        out_mosaic_list.append(out_mosaic)
    return out_mosaic_list

# get extent values of summary polygon dataset (or stream network?)
def get_bbox(in_ply):
    bbox_list = []
    in_driver = ogr.GetDriverByName("ESRI Shapefile")
    in_ds = inDriver.Open(inShapefile, 0)
    in_lyr = in_ds.GetLayer()
    (xmin, xmax, ymin, ymax) = in_lyr.GetExtent()
    bbox_list.append(xmin)
    bbox_list.append(xmax)
    bbox_list.append(ymin)
    bbox_list.append(ymax)
    return bbox_list

# clip all mosaicked LST raster to the bounding box of the rca polygons
### will the RCA polygon dataset be the same extent as the stream dataset?
def clip_mosaic(in_mosaic_list, bbox_list):
    xmin = bbox_list[0]
    xmax = bbox_list[1]
    ymin = bbox_list[2]
    ymax = bbox_list[3]
    for m in in_mosaic_list:
        expr = 'gdalwarp -te %d %d %d %d %s %s' % (xmin, xmax, ymin, ymax, m, )
        os.system(expr)
    return clipped_raster_list

# calculates mean LST values per polygon record, for all daily or 8-day intervals within time period
### one attribute field will added per day interval (i.e. 45 fields for 8-day, and ~365 fields for daily?)
def poly_stat(in_ply, clipped_raster_list):
        # ---
    return summarized_poly


## Generate models (in R)
# use Rpy2 library for Python access to R?
# build models:
# - per basin
# - per RCAs
# - with simple fixed-effects linear, include Julian day
# - with simple fixed-effects linear, no Julian day
# - for whole year
# - for half years

# Output stats for modeling results
## use matplotlib to display graphs on-screen

## Summarize predictions
#

def main():
    pass

if __name__ == '__main__':
    main()
