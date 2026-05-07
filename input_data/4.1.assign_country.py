#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 15:19:22 2023

    Script to allocate the points to country if they fall into the 
    polygon given by the shape file.
    
    The package numba requires python 3.6.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import pandas as pd
import os
import numpy as np
import geopandas as gpd
from time import time
from functions.functions import is_inside_sm_parallel

# =========================================================================
# input data
# =========================================================================
path = './data_csv/'
filename = 'data_nitrogen.csv'
df = pd.read_csv(path+filename)

# world countries
world = gpd.read_file(
    './shapefile_country/world.shp'
    )
country_csv = pd.read_csv(
    './shapefile_country/world.csv'
    )
world['country'] = country_csv['country'].values
crs_orig = world.crs

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
gdf.crs = world.crs

# project data
world_proj = world.to_crs(3857)
gdf_proj = gdf.to_crs(3857)

#%% folders and plot properties
path_file = './data_gdf/'

try:
    os.makedirs(path_file)
except OSError:
    pass

#%% =======================================================================
# Join the points into the countries
# =========================================================================
gdf_proj['country'] = np.nan

points = np.array(list(zip(gdf_proj.geometry.x, gdf_proj.geometry.y)))
countries = world_proj.country.tolist()
N_countries = len(countries)
N_points = len(points)

for i_country in range(N_countries):
    start_time = time()
    
    country = countries[i_country]
    print('# country', i_country+1, '/', N_countries)
    
    geometry = world_proj.loc[world_proj.country==country].geometry
    
    if (geometry.type == 'MultiPolygon').values[0]:
        
        geometry_polygons = [
            geometry_polygon.exterior 
            for geometry_polygon in list(geometry.explode())
            # for geometry_polygon in list(geometry.explode(index_parts=True))
            ]
        
    elif (geometry.type == 'Polygon').values[0]:
        geometry_polygons = [geometry.exterior.values[0]]
    
    N_polygons = len(geometry_polygons)
    bool_mtx = np.zeros([N_points, N_polygons], dtype=bool)
    
    for ipol in range(N_polygons):
        
        geometry_polygon = geometry_polygons[ipol]
        
        x = geometry_polygon.coords.xy[0]
        y = geometry_polygon.coords.xy[1]
        
        polygon = np.array(list(zip(x,y)))
           
        bool_mtx[:,ipol] = is_inside_sm_parallel(points, polygon)[:]      
    
    points_map = bool_mtx.any(axis=1)
    
    print('return', points_map.any())
    print('time', round(time() - start_time,3), 's')
    
    ## check if any point of a country has already been assigned to another
    ## country (even only one point)
    # if yes: create a new column 
    if len(gdf_proj.loc[points_map, 'country'].dropna()) != 0:
        gdf_proj['country_'+country] = np.nan
        gdf_proj.loc[points_map, 'country_'+country] = country
    # if not: assign in basic column
    else:    
        gdf_proj.loc[points_map, 'country'] = country

gdf_out = gdf_proj.to_crs(crs_orig)
gdf_out.to_file(path_file + 'data.geojson', driver='GeoJSON')
gdf_out.to_csv(path_file+'data.csv')
