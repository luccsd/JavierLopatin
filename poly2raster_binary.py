#! /usr/bin/env python

########################################################################################################
#
# BrightnessNormalization.py
#
# A python script to rasterize a shapefile and create a binary raster
#
# Author: Javier Lopatin
# Email: javierlopatin@gmail.com
# Last changes: 07/07/2021
# Version: 1.0
#
# Usage:
#
# python poly2raster_binary.py 
#               -r <Input raster from which copy attributes> 
#               -s <Input shapefile to rasterize> 
#
# example: python poly2raster_binary.py -r raster.tif -s shapefile.shp
#
#
########################################################################################################

import argparse
import geopandas as gpd
import rasterio
from rasterio import features

parser = argparse.ArgumentParser()
parser.add_argument('-r','--inputImage', help='Input raster from which copy attributes', type=str, required=True)
parser.add_argument('-s','--inputShapefile', help='Input polygon-based shapefile to be rasterized', type=str, required=True)
args = vars(parser.parse_args())
    
shp = args['inputShapefile']
raster = args['inputImage']

# Open the shapefile with geopandas
poly = gpd.read_file(shp)

# add column with value 1 for each object
poly = poly.assign(out=1)

# Open raster characteristics
with rasterio.open(raster) as rst:
    #copy and update the metadata from the input raster for the output
    meta = rst.meta.copy()
    meta.update(count=1)

# Now burn the features into the raster and write it out
with rasterio.open(shp[:-4]+'_binary.tif', 'w+', **meta) as out:
    out_arr = out.read(1)
    # this is where we create a generator of geom, value pairs to use in rasterizing
    shapes = ((geom,value) for geom, value in zip(poly.geometry, poly.out))
    burned = features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
    out.write_band(1, burned)
