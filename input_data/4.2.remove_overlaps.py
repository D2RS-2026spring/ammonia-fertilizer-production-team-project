#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 14:21:43 2023

    Script to handle overlap in assignment of points to countries.
    
@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import pandas as pd
import numpy as np
import os

path_in = './data_gdf/'
filename = 'data.csv'
path_out= './data_csv/'
try: 
    os.makedirs(path_out)
except OSError:
    pass

data_in = pd.read_csv(path_in+filename, sep=',', low_memory=False).drop(
    columns=['Unnamed: 0'])
c_ls = [c for c in data_in.columns if 'country_' in c]

sel_cols = [c for c in data_in.columns if c not in c_ls]
data_out = data_in.loc[:, sel_cols]
map_c2 = {}
for c in c_ls:
    
    country2 = c.split('country_')[1]
    print('- country overlap:', country2)
    
    map_c2[country2] =\
        (data_in['country_'+country2]==data_in['country_'+country2])
    data_out.loc[map_c2[country2], 'country'] = country2
        
data_out.to_csv(path_out+'data_country.csv')

#%% check data for some countries
if True:
    import geopandas as gpd
    import matplotlib.pyplot as plt
    
    gdf = gpd.read_file(path_in+'data.shp')
    world = gpd.read_file('./shapefile_country/world.shp')
    country_csv=pd.read_csv('./shapefile_country/world.csv')
    world['country'] = country_csv['country'].values

    c1 = 'United States'
    plt.figure()
    gdf.loc[gdf.country == c1,:].plot(column='nitrogen_c',
                                      markersize=0.1)
    ax = plt.gca()
    world[world.country==c1].boundary.plot(ax=ax, color='k', lw=0.5)
    plt.savefig(c1+'.tif', dpi=500)