#-------------------------------------------------------------------------------
# Name:        steamm.py
# Summary:
#
# Author:      Jesse Langdon
#
# Last Updated:     01/21/2016
# Copyright:   (c) jlangdon 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# import modules
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
proj_dir = raw_input('Enter a new project directory path: ', )

print('Select a MODIS Data Product by entering the product ID (i.e. MOD11A1.005) -')
print('     MOD11A1.005 = Land Surface Temperature/Emissivity Daily L3 Global 1km')
print('     MOD11A2.005 = Land Surface Temperature/Emissivity 8-Day L3 Global 1km')
data_product = raw_input('Enter the MODIS Data Product ID: ', )

process_yr_str = raw_input('Enter year to be processed (i.e. 2015): ', )

print('Enter the MODIS Swath IDs to process (just enter this for now: h09v04,h10v04) -')
swath_id_raw = raw_input('     Swath ID: ')
# temporary solution
swath_id = swath_id_raw.split(',')

print('Please select beginning and end dates, in julian day format (i.e. 1, 365 -')
doy_start_str = raw_input('     Beginning of year: ')
doy_end_str = raw_input('     End of year: ')

print('Please select a drainage polygon shapefile to summarize values (i.e. watersheds, RCAs, etc.): ')
geo_rca = raw_input('Drainage polygon shapefile (enter full path): ')


# do the work
def main(proj_dir, data_product, process_yr_str, swath_id, geo_rca, doy_start_str, doy_end_str, platform = 'MOLT'):

    # Temporary variable conversion
    process_yr = [int(process_yr_str)]
    doy_start = int(doy_start_str)
    doy_end = int(doy_end_str)

    # Set up project directory
    dir_list, source_subdir_list, products_subdir_list = util.create_dir_lists()
    proj_dir_list = util.create_proj_dir_list(proj_dir, dir_list, source_subdir_list, products_subdir_list)
    util.create_new_dir(proj_dir, dir_list, source_subdir_list, products_subdir_list)
    util.create_year_folders(process_yr, proj_dir, dir_list, source_subdir_list)

    # Build tables for HDF files
    dir_hdf = '%s\\%s\\%s\\%s' % (proj_dir, dir_list[0], source_subdir_list[0], process_yr[0])
    util.download_hdf(platform, data_product, process_yr, swath_id, doy_start, doy_end, dir_hdf)
    hdf_filepath_list, hdf_file_list = util.get_hdf_filepaths(dir_hdf)
    hdf_file_array = util.build_file_array(hdf_file_list)
    hdf_date_list = util.get_all_file_dates(hdf_file_array)
    hdf_dates = util.find_dup_file_dates(hdf_date_list)

    # File conversion
    poly_wkt = util.get_proj(geo_rca)
    bbox_list = util.get_bbox(geo_rca)
    geotiff_list = util.convert_hdf(proj_dir, dir_list, hdf_filepath_list, hdf_file_list)
    mosaic_io_array = util.build_mosaic_io_array(geotiff_list, hdf_dates)
    modis_wkt = util.get_modis_wkt("steamm_v01.py")
    vrt_list = util.mosaic_vrt(mosaic_io_array, proj_dir, dir_list, modis_wkt)
    reprj_list = util.reproject_rasters(vrt_list, proj_dir, dir_list, modis_wkt, poly_wkt, bbox_list)
    csv_list = util.LST_to_csv(reprj_list,proj_dir,dir_list)
    acq_date_list = util.build_acq_date_list(csv_list)
    LST_csv = util.build_interpl_table(acq_date_list, proj_dir, dir_list)
    print LST_csv

# testing variables
"""
proj_dir = r'C:\dev\steamm_working\testing\test20160301'
data_product = r'MOD11A1.005'
process_yr = [2015]
swath_id = ['h09v04', 'h10v04']
geo_rca = r'C:\dev\steamm_working\testing\huc6_test.shp'
"""

# call the main function, run the program
if __name__ == '__main__':
    main(proj_dir, data_product, process_yr_str, swath_id, geo_rca, doy_start_str, doy_end_str)