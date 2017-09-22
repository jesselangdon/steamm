#-------------------------------------------------------------------------------------
# Name:         predict_temp.py
#
# Summary:      The predict_temp module using a linear model to predict stream temperatures
#               over a user-defined time period for a discrete stream network. Required inputs
#               include a csv file of interpolated land surface temperature (LST) values, a
#               reach catchment area (RCA) polygon shapefile, and a stream network line shapefile.
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
# Copyright:    (c) South Fork Research, Inc. 2016
# Licence:      FreeBSD License
# Version:      0.1
#-------------------------------------------------------------------------------------

# Input variables

# Drainage polygon shapefile to summarize values (i.e. watersheds, RCAs, etc.): ')
geo_rca =

# Stream network shapefile to which interpolated temperatures will be attached
geo_strm =


def predict_dir_list():
    """Create a list with project directory names."""
    dir_list = ["1source_data", "2temp_files", "3model_output"]
    source_subdir_list = ["1modis_hdf", "2vector_inputs"]
    products_subdir_list = ["1crb_extent", "2polygons", "3stream_network"]
    return dir_list, source_subdir_list, products_subdir_list


def predict_subdir_list(input_dir, dir_list, source_subdir_list, products_subdir_list):
    """Create list of full paths to all project subdirectories."""
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


def predict_create_dir(input_dir, dir_list, source_subdir_list, products_subdir_list):
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


def predict_check_schema(input_dir, proj_dir_list):
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


def predict_create_year_folders(year_list, input_dir, dir_list, source_subdir_list):
    """Add a folder to .\1source_data for each selected year."""
    subdir_hdf = input_dir + "\\" + dir_list[0] + "\\" + source_subdir_list[0]
    for y in year_list:
        os.makedirs(os.path.join(subdir_hdf, str(y)))
    return

def convert_to_vrt(mosaic_io_array, swath_id, input_dir, dir_list, modis_wkt):
    """Generates mosaics as GDAL VRT files for MODIS tiles collected on the same day."""
    print "Generating GDAL VRT files from geotiffs..."
    out_vrt_list = []
    # iterate through list of geotiff file names
    for row in mosaic_io_array:
        if len(swath_id) > 1: # if more than one geotiff in list, mosaic into a vrt file
            in_rasters = ' '.join(row[0:2])
            out_vrt = '%s\\%s\\%s.%s' % (input_dir, dir_list[1], row[2], "vrt")
            expr = 'gdalbuildvrt -a_srs %s %s %s' % (modis_wkt, out_vrt, in_rasters)
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

# File conversion
poly_wkt = util.get_proj(geo_rca)
bbox_list = util.get_bbox(geo_rca)
mosaic_io_array = util.build_mosaic_io_array(geotiff_list, hdf_dates)
modis_wkt = util.get_modis_wkt("steamm.py")
vrt_list = util.convert_to_vrt(mosaic_io_array, swath_id, proj_dir, dir_list, modis_wkt)
reprj_list = util.reproject_rasters(vrt_list, proj_dir, dir_list, modis_wkt, poly_wkt, bbox_list, xres, yres, geo_rca)
csv_list = util.LST_to_csv(reprj_list, proj_dir, dir_list)
acq_date_list = util.build_acq_date_list(csv_list)
LST_csv = util.build_interpl_table(acq_date_list, proj_dir, dir_list)
print LST_csv

# interpolate missing LST values

def interpolate_lst(  ):
    pass

    ###PSEUDO-CODE
    #open LST_value table
    #convert to Numpy array
    #convert zeros to NaN
    #per row, create list of indexes of cells that are NaN
    #use numpy.interp to do interpolation per row
    #fill in first day of values if NaN
    #fill in second to last day if NaN
    #fill in last day if NaN
    #export interpolated array to csv
    return intrp_lst_csv

# convert interpolated LST csv table to grid
def convert_to_grid( ):
    pass
    return grid

# convert LST grid to cell polygon dataset
def grid_to_polygon( ):
    pass
    return polygon

# intersect grid polygon with drainage polygons, merge all attributes
def grid_drain_intersect( ):
    pass
    return polygon


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