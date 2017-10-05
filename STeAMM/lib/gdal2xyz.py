try:
    from osgeo import gdal
except ImportError:
    import gdal

import sys

try:
    import numpy as Numeric
except ImportError:
    import Numeric

def main(srcfile, dstfile, arg = '-csv' ):
    srcwin = None
    skip = 1
    delim = ' '
    band_nums = [1]
    # Open source file.
    srcds = gdal.Open(srcfile)
    if srcds is None:
        print('Could not open %s.' % srcfile)
        sys.exit( 1 )

    bands = []
    for band_num in band_nums:
        band = srcds.GetRasterBand(band_num)
        if band is None:
            print('Could not get band %d' % band_num)
            sys.exit( 1 )
        bands.append(band)

    gt = srcds.GetGeoTransform()

    # Collect information on all the source files.
    if srcwin is None:
        srcwin = (0,0,srcds.RasterXSize,srcds.RasterYSize)

    # Open the output file.
    if dstfile is not None:
        dst_fh = open(dstfile,'wt')
    else:
        dst_fh = sys.stdout

    band_format = (("%g" + delim) * len(bands)).rstrip(delim) + '\n'

    # Setup an appropriate print format.
    if abs(gt[0]) < 180 and abs(gt[3]) < 180 \
       and abs(srcds.RasterXSize * gt[1]) < 180 \
       and abs(srcds.RasterYSize * gt[5]) < 180:
        format = '%.10g' + delim + '%.10g' + delim + '%s'
    else:
        format = '%.3f' + delim + '%.3f' + delim + '%s'

    # Loop emitting data.

    for y in range(srcwin[1],srcwin[1]+srcwin[3],skip):

        data = []
        for band in bands:

            band_data = band.ReadAsArray( srcwin[0], y, srcwin[2], 1 )
            band_data = Numeric.reshape( band_data, (srcwin[2],) )
            data.append(band_data)

        for x_i in range(0,srcwin[2],skip):

            x = x_i + srcwin[0]

            geo_x = gt[0] + (x+0.5) * gt[1] + (y+0.5) * gt[2]
            geo_y = gt[3] + (x+0.5) * gt[4] + (y+0.5) * gt[5]

            x_i_data = []
            for i in range(len(bands)):
                x_i_data.append(data[i][x_i])

            band_str = band_format % tuple(x_i_data)

            line = format % (float(geo_x),float(geo_y), band_str)

            dst_fh.write( line )
    return