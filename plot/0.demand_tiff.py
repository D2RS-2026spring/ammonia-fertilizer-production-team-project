#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 10:51:44 2023

    Script to plot data based on rasterio

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import geopandas as gpd
import pandas as pd
import rasterio
from rasterio import plot
import matplotlib.pyplot as plt
import matplotlib
import rioxarray as rxr
import numpy as np
import os
import matplotlib as mpl
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib

def plot_color_gradient(cmap_name, Nc):
    
    color_index = np.arange(0, Nc)
    gradient = np.linspace(0, 256, Nc)
    gradient = np.vstack((color_index, color_index))
    fig, ax = plt.subplots(figsize=(6.4,.5))
    im = ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(cmap_name))
    plt.yticks([])
    return im

data = {}
filenames = {}
path = '../input_data/data_tif/'
filenames['curr'] = 'ammonia.tif'

path_out = './output/demand_tif/'
try:
    os.makedirs(path_out)
except OSError:
    pass

# 直接读取在线数据，GeoPandas 会自动下载并解析
world = gpd.read_file("https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip")

#%%

with rasterio.open(path+filenames['curr'], 'r+') as rds:
    print('CRS data:', rds.crs)
    print('CRS bounds:', rds.bounds)

Nvalues = {}
Nvalues['curr'] = rxr.open_rasterio(path+filenames['curr'], masked=True)
# convert to ammonia demand (t)
Nvalues['curr'] = Nvalues['curr']

yvals = Nvalues['curr'].values
print('TOT - current', yvals[yvals==yvals].sum()/1e6, 'Mt/y')

data = {}
for key in Nvalues.keys():
    
    try:
        os.makedirs(
            './temp/')        
    except OSError:
        pass

    Nvalues[key].rio.to_raster('./temp/'+key+'.tif') 
    data[key] = rasterio.open('./temp/'+key+'.tif', masked=True)
#%%
if True:
    
    matplotlib.rcParams.update({'font.size': 16})
    
    add_cbar = False
    Nc = 11  
    
    plt.figure()
    figsize = (10,15)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
    bounds = data['curr'].bounds
    extent=[bounds[0], bounds[2],  bounds[1], bounds[3]]
    Nvalues['curr'].values[Nvalues['curr'].values>1e3] = 1e3
    
    # current - sustainable
    cmap = plt.colormaps['magma_r'].resampled(256)
    newcmp = ListedColormap(cmap(np.linspace(0, 0.6, Nc)))
    im = plt.imshow(Nvalues['curr'].values[0,:,:],\
                    cmap=newcmp, extent=extent)

    cbar = plt.colorbar(im, orientation="horizontal",\
             location="top")    
    cbar.set_label("ammonia demand (t/y)", labelpad=15)
    world.boundary.plot(facecolor='none', edgecolor='k', lw=0.2, ax=ax)
    # plt.title('curr')
    plt.ylim([-60, 80])
    plt.xlim([-180, 180])
    plt.savefig(path_out+'demand.tif',
                dpi=500,
                bbox_inches='tight',
                transparent=True)
