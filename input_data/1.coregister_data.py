#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 16:23:29 2023

    Script to resample/coregister tif files based on reference tif file.
    References:
        - https://pygis.io/docs/e_raster_resample.html
    
@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

reproject = True

import rioxarray as rxr
from rasterio.warp import reproject, Resampling, calculate_default_transform
import rasterio
import numpy as np
import os

path_out = './data_tif/'
try: 
    os.makedirs(path_out)
except OSError:
    pass

def reproj_match(infile, match, outfile):
    """
    Reproject a file to match the shape and projection of existing raster. 
    
    Parameters
    ----------
    infile : (string) path to input file to reproject
    match : (string) path to raster with desired shape and projection 
    outfile : (string) path to output file tif
    """
    # open input
    with rasterio.open(infile) as src:
        src_transform = src.transform
        
        # open input to match
        with rasterio.open(match) as match:
            dst_crs = match.crs
            
            # calculate the output transform matrix
            dst_transform, dst_width, dst_height = calculate_default_transform(
                src.crs,     # input CRS
                dst_crs,     # output CRS
                match.width,   # input width
                match.height,  # input height 
                *match.bounds,  # unpacks input outer boundaries (left, bottom, right, top)
            )

        # set properties for output
        dst_kwargs = src.meta.copy()
        dst_kwargs.update({"crs": dst_crs,
                           "transform": dst_transform,
                           "width": dst_width,
                           "height": dst_height,
                           "nodata": 0})
        print("Coregistered to shape:", dst_height, dst_width,'\n Affine',dst_transform)
        # open output
        with rasterio.open(outfile, "w", **dst_kwargs) as dst:
            # iterate through bands and write using reproject function
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)

def check_data(name, data_array):
    """"
    Extract information from .tif files
    """
    
    # metadata raster files
    print('###', name, '###') 
    print("- CRS:", data_array.rio.crs)
    print("- nodatavalue:", data_array.rio.nodata)
    print("- shape:", data_array.shape)
    print("- spatial resolution:", data_array.rio.resolution())
    print("- metadata:", data_array.attrs)
    print("- spatial extent:", data_array.rio.bounds())
    print('######')     
                
data = {}
data_reproj = {}
for variable in [
        'nitrogen_current',
        'solar_potential',
        'solar_to_peak',
        'area_harvest'
        ]:
    
    if variable == 'nitrogen_current':
        
        path = './input_raster/' 
        filename = 'current_syn_nitrogen-2020.tif'
        variable_descr = 'total N - present production' 
    
    elif variable == 'solar_potential':
        
        path = './input_raster/'        
        filename = 'GHI-resampled.tif'
        variable_descr = 'solar irradiation'    

    elif variable == 'area_harvest':
        
        path = './input_raster/'
        filename = 'area-2020.tif'
        variable_descr = 'harvested area'   

    elif variable == 'solar_to_peak':
        
        path = './input_raster/'      
        filename = 'PVOUT-resampled.tif'
        variable_descr = 'solar capacity factor' 
                
    data[variable] = rxr.open_rasterio(path+filename,
                                     masked=True)
    check_data(variable, data[variable])
    
    # reference raster - scarcity_current
    match_reference = './input_raster/current_syn_nitrogen-2020.tif'
    
    if reproject:
        infile = path+filename
        outfile = path_out+filename.split('.')[0]+'-reproj.tif'
        
        reproj_match(infile, match_reference, outfile)
        data_reproj[variable] = rxr.open_rasterio(outfile,
                                         masked=True) 
        
        check_data(path_out+variable, data_reproj[variable])