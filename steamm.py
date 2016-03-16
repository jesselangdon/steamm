#-------------------------------------------------------------------------------
# Name:        steamm.py
# Summary:
#
# Author:      Jesse Langdon
#
# Last Updated:     03/15/2016
# Copyright:   (c) jlangdon 2016
# Licence:      FreeBSD License
#-------------------------------------------------------------------------------

# import modules
import sys
import steamm_util as util

# introduction (temporary)
print('\n')
print('Stream Temperature Automated Modeler using MODIS (STeAMM)')
print('\n')
print('This is an early version of the STeAMM tool, intended strictly for')
print('testing. Please note, this version of the software relies on a command')
print('line interface.  The final version will be in the form a QGIS Plugin.')
print('----------------------------------------------------------------------')
print('\n')


## input variables
print('Enter the name of a new project directory, including the full filepath. STeAMM will ')
print('create a new directory and subdirectory structure, which stores intermediate files')
print('and outputs from the tool.')
proj_dir = raw_input('New project directory filepath and name: ', )

print('\n')
print('Select a MODIS Data Product by entering the product ID (i.e. MOD11A1.005) -')
print('     MOD11A1.005 = Land Surface Temperature/Emissivity Daily L3 Global 1km')
print('     MOD11A2.005 = Land Surface Temperature/Emissivity 8-Day L3 Global 1km')
data_product = raw_input('Enter the MODIS Data Product ID: ', )

print('\n')
process_yr_str = raw_input('Enter year to be processed (i.e. 2015): ', )

print('\n')
print('Enter the MODIS Swath IDs to process (multiple tiles: h09v04,h10v04) -')
swath_id_raw = raw_input('     Swath ID: ')
# temporary solution
swath_id = swath_id_raw.split(',')

print('\n')
print('Please select beginning and end dates, in julian day format (i.e. 1, 365 -')
doy_start_str = raw_input('     Beginning of year: ')
doy_end_str = raw_input('     End of year: ')

print('\n')
print('Please select a drainage polygon shapefile to summarize values (i.e. watersheds, RCAs, etc.): ')
geo_rca = raw_input('Drainage polygon shapefile (enter full path): ')


# do the work
def main(proj_dir, data_product, process_yr_str, swath_id, geo_rca, doy_start_str, doy_end_str, platform = 'MOLT'):

    # Collect inputs into a list for log file
    arg_list = []
    arg_list.append(proj_dir)
    arg_list.append(data_product)
    arg_list.append(process_yr_str)
    arg_list.append(str(swath_id))
    arg_list.append(geo_rca)
    arg_list.append(doy_start_str)
    arg_list.append(doy_end_str)

    # Temporary variable conversion
    process_yr = [int(process_yr_str)]
    doy_start = int(doy_start_str)
    doy_end = int(doy_end_str)

    # Set up project directory
    dir_list, source_subdir_list, products_subdir_list = util.create_dir_lists()
    proj_dir_list = util.create_proj_dir_list(proj_dir, dir_list, source_subdir_list, products_subdir_list)
    util.create_new_dir(proj_dir, dir_list, source_subdir_list, products_subdir_list)
    util.create_year_folders(process_yr, proj_dir, dir_list, source_subdir_list)
    util.log_inputs(proj_dir, arg_list)

    # Build tables for HDF files
    dir_hdf = '%s\\%s\\%s\\%s' % (proj_dir, dir_list[0], source_subdir_list[0], process_yr[0])
    util.download_hdf(platform, data_product, process_yr, swath_id, doy_start, doy_end, dir_hdf)
    hdf_filepath_list, hdf_file_list = util.get_hdf_filepaths(dir_hdf)
    hdf_file_array = util.build_file_array(hdf_file_list)
    hdf_date_list = util.get_all_file_dates(hdf_file_array)
    hdf_dates = util.find_dup_file_dates(hdf_date_list, swath_id)

    # File conversion
    poly_wkt = util.get_proj(geo_rca)
    bbox_list = util.get_bbox(geo_rca)
    geotiff_list, xres, yres = util.convert_hdf(proj_dir, dir_list, hdf_filepath_list, hdf_file_list)
    mosaic_io_array = util.build_mosaic_io_array(geotiff_list, hdf_dates)
    modis_wkt = util.get_modis_wkt("steamm.py")
    vrt_list = util.convert_to_vrt(mosaic_io_array, swath_id, proj_dir, dir_list, modis_wkt)
    reprj_list = util.reproject_rasters(vrt_list, proj_dir, dir_list, modis_wkt, poly_wkt, bbox_list, xres, yres, geo_rca)
    csv_list = util.LST_to_csv(reprj_list, proj_dir, dir_list)
    acq_date_list = util.build_acq_date_list(csv_list)
    LST_csv = util.build_interpl_table(acq_date_list, proj_dir, dir_list)
    print LST_csv

# testing variables
"""
proj_dir = r'C:\dev\steamm_working\testing\test20160311'
data_product = r'MOD11A2.005'
process_yr_str = '2014'
swath_id = ['h08v05']
geo_rca = r'C:\dev\steamm_working\testing\BNG_outline.shp'
doy_start_str = '1'
doy_end_str = '5'
"""


# call the main function, run the program
if __name__ == '__main__':
    main(proj_dir, data_product, process_yr_str, swath_id, geo_rca, doy_start_str, doy_end_str)