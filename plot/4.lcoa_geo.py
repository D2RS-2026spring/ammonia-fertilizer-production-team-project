#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 15:28:11 2023

    Script to plot the global distirbution of LCOA.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""
import os
# 你的Anaconda环境PROJ数据库绝对路径（已验证有效，直接用）
os.environ['PROJ_LIB'] = r"F:\anaconda3\envs\ammonia_repro\Library\share\proj"
os.environ['PROJ_DATA'] = r"F:\anaconda3\envs\ammonia_repro\Library\share\proj"

# 强制初始化pyproj，覆盖所有默认配置
import pyproj
pyproj.datadir.set_data_dir(r"F:\anaconda3\envs\ammonia_repro\Library\share\proj")

# 验证修复是否生效（运行时会打印，成功会显示✅）
try:
    test_crs = pyproj.CRS("EPSG:4326")
    print("✅ PROJ路径修复成功！EPSG:4326正常解析")
except Exception as e:
    print(f"❌ 修复失败，请检查路径: {e}")
# select the system: 
# (i)  agrivolt: supply of electricity from solar panels
# (ii) grid: connected to the grid

system = 'grid'

# select the technology:
# (i) EHB
# (ii) ENR

tech = 'EHB'

print('\n# SYSTEM:', system)
print('# TECH:', tech, '\n')

import matplotlib.pyplot as plt
import matplotlib
import rioxarray as rxr
import geopandas as gpd
import numpy as np
import pandas as pd
import os

path_out = f'./output/lcoa_geo-{system}/'
try:    
    os.makedirs(path_out)    
except OSError:    
    pass

for year in [2020, 2030, 2050]:
    
    filename = f'LCOA_{tech}_EUR_t-{year}.tif'
    
    path_plt = f'../calculation/output/cost-{system}/global_tif/'
    
    raster = rxr.open_rasterio(path_plt+filename)
    
    var = f'LCOA_{tech}_EUR_t-{year}'
    data_frame = raster.to_dataframe(var)
    x = data_frame.index.get_level_values('x')
    y = data_frame.index.get_level_values('y')
    values = data_frame[var].values
    
    map_gzero = (values>0)
    df = pd.DataFrame()
    df[var] = values[map_gzero]
    gdf_ey = gpd.GeoDataFrame(
        df, geometry = gpd.points_from_xy(x[map_gzero], y[map_gzero]))
    
    #%%
    
    vmax = 3250
    vmin = 250
    bounds = np.linspace(vmin, vmax, 9)
    norm = matplotlib.colors.BoundaryNorm(bounds, 256)
    
    world = gpd.read_file(
        '../input_data/shapefile_country/world.shp'
        )
    
    plt_style = {
        'column':var,
        'markersize':0.1,
        'cmap':'YlOrRd',
        'norm':norm
        }
    
    plt.figure()
    # world.plot(color='tab:grey', linewidth=0.05, alpha=0.5)
    ax = plt.gca()
    plt_style['ax'] = ax
    gdf_ey[gdf_ey[var]>0].plot(**plt_style)
    ax = plt.gca()
    world.boundary.plot(ax=ax, color='k', linewidth=0.05)
    plt.ylim([-45, 60])
    
    vmin, vmax = gdf_ey[var].min(), gdf_ey[var].max()
    fig = plt.gcf()
    cax = fig.add_axes([1, 0.1, 0.03, 0.8])
    sm = plt.cm.ScalarMappable(cmap=plt_style['cmap'],
                               norm=norm)
    sm._A = []
    cbr = fig.colorbar(sm, cax=cax,)
    cbr.ax.tick_params(labelsize=20)
        
    plt.savefig(path_out+filename,
                dpi=800,
                bbox_inches='tight',
                transparent=True)