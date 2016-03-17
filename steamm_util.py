#-------------------------------------------------------------------------------------
# Name:         steamm_util.py
#
# Summary:      STeAMM (Stream Temperature Automated Modeler using MODIS) is a QGIS
#               Plugin that automates the process of modeling stream temperature using
#               the methodology described in McNyset, et al. 2015. STeAMM is written
#               in Python, and relies on several external libraries, including gdal,
#               numpy, matplotlib, and PyQT.  Specifically the steamm_util.py file
#               includes classes, methods, and functions that are used by the main
#               function in steamm.py and the form.ui PyQT form.
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
#
# Version:      0.3
#-------------------------------------------------------------------------------------

"""STeAMM (Stream Temperature Automated Modeler using MODIS) is a QGIS Plugin that
automates the process of modeling stream temperature using the methodology described
in McNyset, et al. 2015. STeAMM is written in Python, and relies on several external
libraries, including gdal, numpy, matplotlib, and PyQT.  Specifically the steamm_util.py
file includes classes, methods, and functions that are used by the main function in
steamm.py and the form.ui PyQT form."""

# import modules
import os
import shutil
import get_modis as gm
import gdal
import gdalconst
import ogr
import csv


# ----------------------
# class projectDir

def create_dir_lists():
    """Create a list with project directory names."""
    dir_list = ["1source_data", "2temp_files", "3model_output"]
    source_subdir_list = ["1modis_hdf", "2vector_inputs"]
    products_subdir_list = ["1crb_extent", "2polygons", "3stream_network"]
    return dir_list, source_subdir_list, products_subdir_list


def create_proj_dir_list(input_dir, dir_list, source_subdir_list, products_subdir_list):
    """Create list of full paths to all project directories."""
    proj_dir_list = []
    for d in dir_list:
        proj_dir_list.append(input_dir + "\\" + d)
    # create sub-directories for 1source_data folder
    for s in source_subdir_list:
        proj_dir_list.append(input_dir + "\\" + dir_list[0] + "\\" + s)
    # create sub-directories for 3products folder
    for p in products_subdir_list:
        proj_dir_list.append(input_dir + "\\" + dir_list[2] + "\\" + p)
    print "Project directory list created..."
    return proj_dir_list


def create_new_dir(input_dir, dir_list, source_subdir_list, products_subdir_list):
    """Create new project directory using STeAMM project directory schema."""
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print "Project directory created..."
    else:
        shutil.rmtree(input_dir)
        os.makedirs(input_dir)
        print "Project directory already exists! Overwriting..."
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
    return


def check_dir_schema(input_dir, proj_dir_list):
    """If the "existing project" option is selected in the plugin form, check if directory with STeAMM schema exists."""
    user_dir_list = []
    missing_dir_list = []
    for user_root, user_dir, user_files in os.\
            walk(input_dir):
        for d in user_dir:
            user_dir_list.append(os.path.join(user_root, d))
    for ideal_dir in proj_dir_list:
        if ideal_dir not in user_dir_list:
            missing_dir_list.append(ideal_dir)
    if len(missing_dir_list) >= 1:
        message = "Missing directories: %s" % (str(missing_dir_list))
    else:
        message = "All required directories are present."
    return message


def create_year_folders(year_list, input_dir, dir_list, source_subdir_list):
    """Add a folder to .\1source_data for each selected year."""
    subdir_hdf = input_dir + "\\" + dir_list[0] + "\\" + source_subdir_list[0]
    for y in year_list:
        os.makedirs(os.path.join(subdir_hdf, str(y)))
    return


def log_inputs(proj_dir, arg_list):
    logfile_path = '%s\\%s' % (proj_dir, "logfile.txt")
    logfile = open(logfile_path, "w")
    logfile.write("\n".join(arg_list))
    logfile.close()
    return


# --------------------
# class buildHDFtables
def download_hdf(platform, product, year_list, tile_list, doy_start, doy_end, dir_hdf, proxy=None):
    """download HDF files for multiple years, using get_modis."""
    for year in year_list:
        for tile in tile_list:
            gm.get_modisfiles(platform, product, year, tile, proxy, doy_start, doy_end, dir_hdf)
        message = 'All HDF files downloaded for %d.' % (year)
        print message
    return


def get_hdf_filepaths(hdf_dir):
    """Get a list of HDF files downloaded by get_modis.py, which is be used for iterating through hdf file conversion."""
    print "Building list of downloaded HDF files..."
    hdf_file_list = []
    hdf_filepath_list = []
    for dir_path, subdir, files in os.walk(hdf_dir):
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


def get_all_file_dates(hdf_file_array):
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


# --------------------
# class convertLST
def convert_hdf(input_dir, dir_list, hdf_filepath_list, hdf_file_list):
    global src_xres
    global src_yres
    """Converts MODIS HDF files to a geotiff format."""
    print "Converting MODIS HDF files to geotiff format..."
    out_format = 'GTiff'
    out_dir = dir_list[1]  # .\2temp_files
    local_array = zip(hdf_filepath_list, hdf_file_list)
    out_geotiff_list = []

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
        out_file = "%s\\%s\\%s.%s" % (input_dir, out_dir, out_filename, "tif")
        out_geotiff = driver.Create(out_file, src_cols, src_rows, src_band_count, gdal.GDT_Float32)
        out_geotiff.SetGeoTransform(src_geotransform)
        out_geotiff.SetProjection(src_proj)
        out_geotiff.GetRasterBand(1).WriteArray(src_array)
        out_geotiff.FlushCache()

        # Create list of output geotiffs
        out_geotiff_list.append(out_file)

    return out_geotiff_list, src_xres, src_yres


def get_proj(in_poly):
    """Obtain the projection of the drainage polygon dataset as a WKT projection file."""
    print "Getting projection of drainage polygon dataset..."
    driver = ogr.GetDriverByName('ESRI Shapefile')
    open_poly = driver.Open(in_poly)
    lyr = open_poly.GetLayer()
    spatialRef = lyr.GetSpatialRef()
    poly_proj4 = spatialRef.ExportToProj4()
    poly_wkt = '"' + poly_proj4 + '"'
    return poly_wkt


def build_mosaic_io_array(in_geotiff_list, hdf_dates):
    """Builds an array with each list item consisting of 1) file names with duplicate name, and 2) shared collection date."""
    print "Building input/output array from mosaic files..."
    mosaic_io_array = []
    for date in hdf_dates:
        row = [i for i in in_geotiff_list if date in i]
        row.append(date)
        mosaic_io_array.append(row)
    return mosaic_io_array


def get_modis_wkt(steamm_script):
    """Returns the filepath to the MODIS Sin WKT projection file"""
    print "Finding the file path to the MODIS WKT projection file..."
    steamm_path = os.path.abspath(steamm_script)
    steamm_dir = os.path.dirname(steamm_path)
    modis_wkt_filepath = os.path.join(steamm_dir, "MODIS_sin.wkt")
    return modis_wkt_filepath


def convert_to_vrt(mosaic_io_array, swath_id, input_dir, dir_list, modis_wkt):
    """Generates mosaics as GDAL VRT files for MODIS tiles collected on the same day."""
    print "Generating GDAL VRT files from geotiffs..."
    out_vrt_list = []
    # iterate through list of geotiff file names
    for row in mosaic_io_array:
        if len(swath_id) > 1: # if more than one geotiff in list, mosaic into a vrt file
            in_rasters = ' '.join(row[0:2])
            out_vrt = '%s\\%s\\%s.%s' % (input_dir, dir_list[1], row[2], "vrt")
            expr = 'gdalbuildvrt -of %s -a_srs %s %s %s' % ("VRT", modis_wkt, out_vrt, in_rasters)
        else: # otherwise, just convert the geotiff to a vrt file
            out_vrt = '%s\\%s\\%s.%s' % (input_dir, dir_list[1], row[1], "vrt")
            expr = 'gdal_translate -of %s -a_srs %s %s %s' % ("VRT", modis_wkt, row[0], out_vrt)
        os.system(expr)
        out_vrt_list.append(out_vrt)
    return out_vrt_list


def get_bbox(in_poly):
    """Gets the extent envelope values of drainage polygons."""
    print "Calculating the extent envelope vaues of drainage polygon dataset..."
    bbox_list = []
    in_driver = ogr.GetDriverByName("ESRI Shapefile")
    in_ds = in_driver.Open(in_poly, 0)
    in_lyr = in_ds.GetLayer()
    (xmin, xmax, ymin, ymax) = in_lyr.GetExtent()
    bbox_list.append(xmin)
    bbox_list.append(xmax)
    bbox_list.append(ymin)
    bbox_list.append(ymax)
    return bbox_list


def reproject_rasters(in_vrt_list, input_dir, dir_list, modis_wkt, poly_wkt, bbox_list, xres, yres, in_ply):
    """Re-projects VRT mosaics to same projection as drainage polygons, then clips extent to polygon envelope."""
    print "Reprojecting VRT mosaics..."
    xmin = bbox_list[0]
    xmax = bbox_list[1]
    ymin = bbox_list[2]
    ymax = bbox_list[3]
    out_reprj_list = []
    for in_vrt in in_vrt_list:
        out_file = '%s_%s.%s' % (in_vrt, "reprj", 'tif')
        expr = 'gdalwarp -overwrite -t_srs %s -tr %f %f -r %s -of %s -dstnodata %d -cutline %s -cblend %d %s %s' % \
               (poly_wkt, xres, yres, 'bilinear', 'GTiff', -999, in_ply, 5, in_vrt, out_file)
        """
        expr = 'gdalwarp -overwrite -t_srs %s -te %f %f %f %f -tr %f %f -r %s -of %s -dstnodata %d -cutline %s %s %s' % \
               (poly_wkt, xmin, ymin, xmax, ymax, xres, yres, 'bilinear', 'GTiff', 0, in_ply, in_vrt, out_file)
        """
        os.system(expr)
        out_reprj_list.append(out_file)
    return out_reprj_list


# get julian date from the mosaicked geotiff file name array
def get_first_acq_date(mosaic_io_array):
    acq_year = mosaic_io_array[0][1]
    acq_date = acq_year[5:8]
    return acq_date


# Convert LST geotiffs to csv files
def LST_to_csv(in_reprj_list, input_dir, dir_list):
    """Converts mosaicked, reprojected LST geotiffs into tables in
    a CSV file format."""
    print "Converting geotiffs to csv files..."
    import gdal2xyz
    out_csv_list = []
    for tif_file in in_reprj_list:
        tif_name_split = tif_file.split('.')
        acq_date = tif_name_split[0][-3:]
        xyz_filename = '%s_%s.%s' % (tif_name_split[0], 'xyz', 'csv')
        csv_filename = '%s_%s.%s' % (tif_name_split[0], 'tbl', 'csv')
        gdal2xyz.main(tif_file, xyz_filename)
        with open (xyz_filename, 'rb') as input, open(csv_filename, 'wb') as output:
            reader = csv.reader(input, delimiter = ' ')
            writer = csv.writer(output, delimiter = ',', quoting = csv.QUOTE_NONNUMERIC )
            all_rows = []
            all_rows.insert(0, ["UID", "X", "Y", str(acq_date)])
            row = next(reader)
            for i, row in enumerate(reader):
                if row[2] != '-999':
                    all_rows.append([str(i + 1)] + row)
            writer.writerows(all_rows)
        out_csv_list.append(csv_filename)
    return out_csv_list


# build a list with julian dates of tile and csv table file paths
def build_acq_date_list(in_csv_list):
    """Builds an array made up of julian dates paired with csv files."""
    print "Building acquisition date list..."
    acq_date_list = []
    for csv in in_csv_list:
        csv_filepath_list = csv.split('.')
        acq_date = csv_filepath_list[0][-7:-4]
        acq_year = csv_filepath_list[0][-11:-7]
        row = [acq_date, acq_year, csv]
        acq_date_list.append(row)
    return acq_date_list


# build csv table to serve as input to LST interpolation process
def build_interpl_table(acq_date_list, input_dir, dir_list):
    """Builds a csv table comprised of grid cell LST values from
    each tile.  The csv table will serve as input to the LST value
    interpolation process."""
    print "Building LST interpolation input table..."
    acq_year = acq_date_list[0][1]
    out_dir = '%s\\%s\\' % (input_dir, dir_list[1])
    out_file = '%s%s_%s.%s' % (out_dir, 'LST', acq_year, 'csv')
    first_filename = acq_date_list[0][2]
    file1_rows = []

    with open(first_filename, 'rb') as file1:
        reader1 = csv.reader(file1)
        for r1 in reader1:
            file1_rows.append(r1)

    for acq_date in acq_date_list[1:]: #skips the first csv file in list
        with open(acq_date[2], 'rb') as fileX:
            readerX = csv.reader(fileX, delimiter = ',')
            fileX_rows = []
            for rX in readerX:
                fileX_rows.append(rX)
            LST_col_list = [row[3] for row in fileX_rows]
            for (f1,LST_val) in zip(file1_rows, LST_col_list):
                f1.append(LST_val)

    with open(out_file, 'wb') as out_csv:
        writer = csv.writer(out_csv, delimiter = ',')
        for f in file1_rows:
            writer.writerow(f)
    print "Data pre-processing complete!"
    return out_csv


# --------------------
# class modelLST
# interpolate missing LST values
### this is currently accomplished using Kris's R code. May need to be ported to Numpy?
def interpolate_lst(  ):
    pass
    return intrp_lst_list


# calculates mean LST values per polygon record, for all daily or 8-day intervals within time period
### one attribute field will added per day interval (i.e. 45 fields for 8-day, and ~365 fields for daily?)
def poly_stat(in_ply, clipped_raster_list):
    pass
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

