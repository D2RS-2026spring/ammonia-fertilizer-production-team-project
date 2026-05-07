#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 7 08:06:19 2023

    Script to combine LCOA calculation per year as cumulative curve
    and in maps.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

# select the system: 
# (i)  agrivolt: supply of electricity from solar panels
# (ii) grid: connected to the grid

system = 'grid'

print('\n# SYSTEM:', system, '\n')

paths = {
    'ammonia':'../input_data/data_tif/',
    'LCOE_PV_2020':f'../calculation/output/cost-{system}/global_tif/',
    'LCOE_PV_2050':f'../calculation/output/cost-{system}/global_tif/',
    'LCOA_EHB_2020':f'../calculation/output/cost-{system}/global_tif/',
    'LCOA_ENR_2020':f'../calculation/output/cost-{system}/global_tif/',
    'LCOA_EHB_2030':f'../calculation/output/cost-{system}/global_tif/',
    'LCOA_ENR_2030':f'../calculation/output/cost-{system}/global_tif/',
    'LCOA_EHB_2050':f'../calculation/output/cost-{system}/global_tif/',
    'LCOA_ENR_2050':f'../calculation/output/cost-{system}/global_tif/',
    }
filenames = {
    'ammonia':'ammonia.tif',
    'LCOE_PV_2020':'LCOE_PV_EUR_MWh-2020.tif',
    'LCOE_PV_2050':'LCOE_PV_EUR_MWh-2050.tif',
    'LCOA_EHB_2020':'LCOA_EHB_EUR_t-2020.tif',
    'LCOA_ENR_2020':'LCOA_ENR_EUR_t-2020.tif',
    'LCOA_EHB_2030':'LCOA_EHB_EUR_t-2030.tif',
    'LCOA_ENR_2030':'LCOA_ENR_EUR_t-2030.tif',    
    'LCOA_EHB_2050':'LCOA_EHB_EUR_t-2050.tif',
    'LCOA_ENR_2050':'LCOA_ENR_EUR_t-2050.tif'
    }  

import rasterio
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib import cm
import os

path_out = f'./output/cumulative-{system}/'
try:
    os.makedirs(path_out)
except OSError:
    pass

NH3_prices = pd.read_excel('../calculation/input/ammonia_prices.xlsx',
                           engine='openpyxl', index_col='date')
# U.S. dollars per metric ton
p_ref_ls = NH3_prices.price.values

data_raster = {}
data_mtx = {}
for var in filenames.keys():
    
    data_raster[var] = rasterio.open(
        paths[var]+filenames[var], masked=True)

    data_mtx[var] = data_raster[var].read()

df_out = pd.DataFrame()

world = gpd.read_file('../input_data/shapefile_country/world.shp')

map_nonan = (data_mtx['ammonia'] == data_mtx['ammonia'])
tot_NH3_dem = data_mtx['ammonia'][map_nonan].sum()

# remove data above threshold of price and compute the associated total demand
lcoa_ref_arr = np.arange(100, 3251, 50)
data_arr = {}

# map points above thrshold
dict_map_ab_thr_raw = {}
 
for tech in ['ENR', 'EHB']:
    for ip_ref in range(len(p_ref_ls)):
        for year in [2050, 2030, 2020]:                

            key = f'ammonia_{tech}_{year}_{ip_ref}'
            
            data_mtx[f'ammonia-bthr_{tech}_{year}_{ip_ref}'] =\
                data_mtx['ammonia'].copy()
                
            data_mtx[f'LCOA-bthr_{tech}_{year}_{ip_ref}'] =\
                data_mtx[f'LCOA_{tech}_{year}'].copy()                    
                                
            # map prices below reference values
            _map_below_thr = data_mtx[f'LCOA_{tech}_{year}'] < p_ref_ls[ip_ref]                
            dict_map_ab_thr_raw[key] = ~_map_below_thr
            
            data_mtx[f'ammonia-bthr_{tech}_{year}_{ip_ref}'][~_map_below_thr] = np.nan
            data_mtx[f'LCOA-bthr_{tech}_{year}_{ip_ref}'][~_map_below_thr] = np.nan
            
            _mapNH3 = data_mtx[f'ammonia-bthr_{tech}_{year}_{ip_ref}']==\
                data_mtx[f'ammonia-bthr_{tech}_{year}_{ip_ref}']
            total_NH3 =\
                data_mtx[f'ammonia-bthr_{tech}_{year}_{ip_ref}'][_mapNH3].sum()
            
            print(f'- {key}:', 
                  'SUPPLY:', round(total_NH3/1e6,1), 'Mt/y',
                  'DEMAND:', round(tot_NH3_dem/1e6,1), 'Mt/y',
                  round(total_NH3/tot_NH3_dem*100,3), '%')
            
            df_out.loc[key, 'Mt/y - SUP'] = round(total_NH3/1e6,1)
            df_out.loc[key, 'Mt/y - DEM'] = round(tot_NH3_dem/1e6,1)
            df_out.loc[key, '%'] = round(total_NH3/tot_NH3_dem*100,1)
            
            data_arr[key] = np.zeros(len(lcoa_ref_arr))  
            for idx_thr in np.arange(len(lcoa_ref_arr)):
                
                p_thr = lcoa_ref_arr[idx_thr]
                mtx_dem = data_mtx['ammonia'].copy()
                _map_below_thr = data_mtx[f'LCOA_{tech}_{year}'] < p_thr
                mtx_dem[~_map_below_thr] = np.nan
                
                data_arr[key][idx_thr] = mtx_dem[mtx_dem==mtx_dem].sum()

# convert year-specific points below threshold to tech-, dem-, thr- specific
dict_map_ab_thr = {}  
for tech in ['ENR', 'EHB']:
    for ip_ref in range(len(p_ref_ls)):
        key = f'ammonia_{tech}_{ip_ref}'
        dict_map_ab_thr[key] = dict_map_ab_thr_raw[f'ammonia_{tech}_2020_{ip_ref}']
        for year in [2050, 2030]:  
            key_raw = f'ammonia_{tech}_{year}_{ip_ref}'
            # collect the points that are above the thresholds in every year
            dict_map_ab_thr[key] =\
                (dict_map_ab_thr[key] & dict_map_ab_thr_raw[key_raw])
        
        _temp_mtx = data_mtx['ammonia'][dict_map_ab_thr[key]]
        tot_ab_thr = _temp_mtx[_temp_mtx==_temp_mtx].sum()
        delta = tot_NH3_dem - tot_ab_thr
        print(f'- AB. THR. {key}:',
              round(tot_ab_thr/1e6,1),
              'SATISFIED', round(delta/1e6,1)
              )
df_out.to_csv(path_out+'/df_out-NH3.csv')

#%% cumulative demand curve with variation depending on price threshold        
import matplotlib
matplotlib.rcParams.update({'font.size': 20})
    
col_dict = {
    2020:'#c73818',
    2030:'#1938b3',
    2050:'#039130'
    }
maps_dict = {
    2020:'Reds',
    2030:'Blues',
    2050:'Greens',
    }
ls_dict = {
    'ENR':'-',
    'EHB':'-'
    }
dict_minmax = {
    2020: (750, 2000),
    2030: (500,  1750),
    2050: (250, 1500),
    }

for tech in ['ENR', 'EHB']:
    
    plt.figure(figsize=(10,6))

    for year in [2020, 2030, 2050]:
        
        for ip_ref in range(len(p_ref_ls)):
        
            key = f'ammonia_{tech}_{year}_{ip_ref}'

            x = data_arr[key]/1e6
            y = lcoa_ref_arr    
            plt.plot(y, x, label = ' '.join(key.split('_')), lw= 10,
                     ls=ls_dict[tech], c=col_dict[year])
        
    plt.xticks(np.arange(250, 3251, 250), rotation = 90)
    plt.xlabel('price of ammonia (EUR/t$_{NH3}$)')
    plt.ylabel('demand (Mt$_{NH3}$)')
    xlim = [250, 3251]
    plt.xlim(xlim)

    map_nonan = (data_mtx['ammonia'] == data_mtx['ammonia'])
    tot_NH3_dem = data_mtx['ammonia'][map_nonan].sum()
    ydem = tot_NH3_dem/1e6
    plt.plot(xlim, [ydem]*2, lw=3, c='tab:grey',
              ls='dotted')
        
    plt.ylim([-5, 175])
    
    plt.yticks(np.arange(0, 176, 25))
    
    ylim = plt.ylim()        
    
    for ip_ref in range(len(p_ref_ls)):
        if ip_ref in [0, 2, 3]:
            plt.plot([p_ref_ls[ip_ref]]*2, ylim, c='tab:grey', lw=3, ls='-.')
    
    plt.savefig(path_out+f'/demand_fraction-{tech}.png',
                dpi=600,
                bbox_inches='tight',
                transparent=True)
        
#%% map demand below a threshold per year and per technology

if False:
    figsize = (10,5)
    
    new_cmap_dict = {}
    for tech in ['ENR', 'EHB']:
        for ip_ref in range(len(p_ref_ls)):
    
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
            
            bounds = data_raster[f'LCOA_{tech}_{year}'].bounds
            extent=[bounds[0], bounds[2], bounds[1], bounds[3]]  
            res = 0.083333
            x_arr = np.arange(bounds[0], bounds[2]-2*res, res)
            y_arr = np.arange(bounds[1], bounds[3]-res, res)
            
            x_mtx = np.ones([len(y_arr),1])@x_arr[np.newaxis,...]
            y_mtx = y_arr[...,np.newaxis]@np.ones([1,len(x_arr)])
            
            vmin = 0
            vmax = 1
            Nc = 3
            central_col = 0.1      
            nodes = ([0, (central_col-vmin)/(vmax-vmin), 1],\
                      [round(vmin,1), 1, round(vmax,1)])
            colors=['k', 'k', '#c5c6c7']
            my_cmap =\
                mpl.colors.LinearSegmentedColormap.from_list("mycmap",\
                list(zip(nodes[0], colors)), Nc) 
                
            data_ws = data_mtx['ammonia'].copy().astype(float)
            data_ws[data_ws!=1.0] = np.nan
            
            im1 = ax.imshow(data_ws[0,:,:],\
                vmin=vmin, vmax=vmax,\
                extent=extent, aspect='auto', cmap=my_cmap) 
    
            ##
            
            ## PLOT UNSATISIFED DEMAND
            
            key = f'ammonia_{tech}_{ip_ref}'                    
            unsat_dem_mtx =\
                data_mtx['ammonia'].copy()
            unsat_dem_mtx[dict_map_ab_thr[key]] = 1
            unsat_dem_mtx[~dict_map_ab_thr[key]] = np.nan
            
            # ax = plt.gca()
            im3 = ax.imshow(unsat_dem_mtx[0,:,:],
                            extent=extent, aspect='auto',
                            cmap='cividis_r')
    
            ##                
            
            for year in [2050, 2030, 2020]:        
                
                ax = plt.gca()
                key = f'ammonia_{tech}_{year}_{ip_ref}'                                               
                                
                ## PLOT ECONOMIC POINTS PER TECHNOLOGY PER SCENARIO
                ## VARY DEMAND COLOR PER YEAR
                
                data_mtx_cp_N =\
                    data_mtx[f'ammonia-bthr_{tech}_{year}_{ip_ref}'].copy()                        
                data_mtx_cp_N[data_mtx_cp_N<1e-6] = np.nan  
                
                data_mtx_cp_L =\
                    data_mtx[f'LCOA-bthr_{tech}_{year}_{ip_ref}'].copy()                                                
                data_mtx_cp_L[data_mtx_cp_L<1e-6] = np.nan    
                
                data_mtx_cp = data_mtx_cp_L
    
                my_cmap = maps_dict[year]
                cmap = cm.get_cmap(my_cmap, 256)
                newcmp = ListedColormap(cmap(np.linspace(0.2, 1, 10))) 
                new_cmap_dict[year] = newcmp
                
                ## remove points above and below SolarAtlas domain
                # data_mtx_cp[0,:,:][y_mtx>60] = np.nan
                # data_mtx_cp[0,:,:][y_mtx<-45] = np.nan
                # data_mtx_cp[0,:,:][x_mtx>180] = np.nan
                # data_mtx_cp[0,:,:][x_mtx<-180] = np.nan  
                  
                _mapNH3 = data_mtx_cp_N==data_mtx_cp_N
                total_NH3 = data_mtx_cp_N[_mapNH3].sum()
                
                _pref = p_ref_ls[ip_ref]
                valTot = total_NH3/1e9
                valTotPerc = total_NH3/tot_NH3_dem*100
                print(f'* {key}: {valTot:.2f} Mt/y', f'{valTotPerc:.2f} %')
                try:
                    valMax = data_mtx_cp[data_mtx_cp==data_mtx_cp].max()
                    valAvg = data_mtx_cp[data_mtx_cp==data_mtx_cp].mean()
                    valMin = data_mtx_cp[data_mtx_cp==data_mtx_cp].min()
                    print('\t range LCOA <'+f' {_pref}:',
                          f'max - {valMax:.2f}',
                          f'avg - {valAvg:.2f}',
                          f'min - {valMin:.2f}',
                          )
                except ValueError:
                    pass
                
                vmin, vmax = dict_minmax[year][0], dict_minmax[year][1]
                    
                im2 = ax.imshow(data_mtx_cp[0,:,:],\
                    vmin=vmin, vmax=vmax,\
                    extent=extent, aspect='auto', cmap=newcmp)                      
            
            plt.xlim([-180, 180])
            plt.ylim([-45, 60])
    
            world.boundary.plot(facecolor='none',
                                edgecolor='k', lw=0.2, ax=ax)
            
            plt.xticks([])
            plt.yticks([])
            plt.savefig(path_out+f'map_econ-{tech}_{ip_ref}'+'.tif',
                        dpi=300,
                        bbox_inches='tight',
                        transparent=True)
                
    #%%
    for year in [2020, 2030, 2050]:
        
        vmin, vmax = dict_minmax[year][0], dict_minmax[year][1]
        
        plt.figure()
        im = plt.imshow([[0],[10]],
                   cmap=plt.get_cmap(new_cmap_dict[year], 10), 
                   vmin = vmin,
                   vmax = vmax
                   )
        plt.colorbar(
            aspect = 7
            )                
        plt.savefig(path_out+f'colorbar-{year}'+'.tif',
                    dpi=300,
                    bbox_inches='tight',
                    transparent=True)    
                    
                
                