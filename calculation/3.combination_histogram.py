#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 08:32:49 2023

    Script to combine LCOA calculation per year in dataframe at country level.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

# select the system: 
# (i)  agrivolt: supply of electricity from solar panels
# (ii) grid: connected to the grid

system = 'agrivolt'

paths = {
    'nitrogen':'../input_data/data_tif/',
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
    'nitrogen':'current_syn_nitrogen-2020-reproj.tif',
    'LCOE_PV_2020':'LCOE_PV_EUR_MWh-2020.tif',
    'LCOE_PV_2050':'LCOE_PV_EUR_MWh-2050.tif',
    'LCOA_EHB_2020':'LCOA_EHB_EUR_t-2020.tif',
    'LCOA_ENR_2020':'LCOA_ENR_EUR_t-2020.tif',
    'LCOA_EHB_2030':'LCOA_EHB_EUR_t-2030.tif',
    'LCOA_ENR_2030':'LCOA_ENR_EUR_t-2030.tif',    
    'LCOA_EHB_2050':'LCOA_EHB_EUR_t-2050.tif',
    'LCOA_ENR_2050':'LCOA_ENR_EUR_t-2050.tif'
    }  

import rioxarray as rxr
import numpy as np
import pandas as pd
import os
import geopandas as gpd

print('# SYSTEM:', system)

NH3_prices = pd.read_excel('./input/ammonia_prices.xlsx',
                           engine='openpyxl', index_col='date')
# U.S. dollars per metric ton
p_ref_ls = NH3_prices.price.values.tolist()

year_ls = [2050, 2030, 2020]

print('*** reading rasters...')
data_raster = {}
data_mtx = {}
for var in filenames.keys():
    
    print('\t', var)
    
    data_raster[var] = rxr.open_rasterio(paths[var]+filenames[var],\
                                         masked=True)

    data_mtx[var] = data_raster[var].values

lcoa_ref_arr = np.arange(100, 2501, 50)

print('*** reading world .shp...')
world = gpd.read_file(
    '../input_data/shapefile_country/world.shp'
    )
# convert nitrogen demand to ammonia demand
data_mtx['ammonia'] = data_mtx['nitrogen']*17/14

print('*** creating ammonia .tif...')
data_raster['ammonia'] = data_raster['nitrogen'].copy()
data_raster['ammonia'].values[:,:,:] = data_mtx['ammonia'][:,:,:]
data_raster['ammonia'].rio.to_raster(paths['nitrogen']+'ammonia.tif',
    driver='GTIFF') 

tot_NH3_dem = {} 
data_mtx['ammonia'] = data_mtx['ammonia'].copy()
_map_nonan = (data_mtx['ammonia']==data_mtx['ammonia'])
tot_NH3_dem['ammonia'] = data_mtx['ammonia'][_map_nonan].sum()   

print('- copying raster...')
for tech in ['ENR', 'EHB']:
    for year in year_ls:
        
        data_mtx[f'LCOA_{tech}_{year}'] =\
            data_mtx[f'LCOA_{tech}_{year}'].copy()

# reference map
print('*** reading reference nan file...')
path_nonan = '../input_data/data_tif/'
raster_nonan = rxr.open_rasterio(\
     path_nonan+'current_syn_nitrogen-2020-reproj.tif', masked=True)
rds = raster_nonan.squeeze().drop("spatial_ref").drop("band")
rds.name = 'ref'
df_nonan = rds.to_dataframe().reset_index()

# country dataframe
path_in = '../input_data/data_csv/'
country_df = pd.read_csv(path_in+'data_country.csv')

#%%
# remove data above threshold of price and compute the associated total demand
data_df = pd.DataFrame()

print('*** remove above threshold')
for tech in ['ENR', 'EHB']:
    print('- technology:', tech)
    for ip_ref in range(len(p_ref_ls)):
        
        print('- price:', p_ref_ls[ip_ref], ip_ref+1, '/', len(p_ref_ls))
        
        data_mtx[f'ammonia-athr_{tech}_{ip_ref}'] =\
            data_mtx['ammonia'].copy()
            
        data_mtx[f'LCOA-athr_{tech}_{ip_ref}'] =\
            data_mtx[f'LCOA_{tech}_{year}'].copy()  
                
        for year in year_ls:
            
               
            key = f'{tech}_{year}_{ip_ref}'
            
            data_mtx[f'ammonia-bthr_{tech}_{year}_{ip_ref}'] =\
                data_mtx['ammonia'].copy()
                
            data_mtx[f'LCOA-bthr_{tech}_{year}_{ip_ref}'] =\
                data_mtx[f'LCOA_{tech}_{year}'].copy()                    
                                                
            # map prices below reference values
            if year == 2020:
                
                _map_range_thr = (data_mtx[f'LCOA_{tech}_2020']\
                                  <= p_ref_ls[ip_ref])
                
            elif year == 2030:
                
                _map_range_thr_m1 =\
                (data_mtx[f'LCOA_{tech}_2020'] > p_ref_ls[ip_ref])
                _map_range_thr_1 =\
                (data_mtx[f'LCOA_{tech}_{year}'] <= p_ref_ls[ip_ref])
                _map_range_thr = (_map_range_thr_m1 & _map_range_thr_1)
                
            elif year == 2050:

                 _map_range_thr_m2 =\
                     (data_mtx[f'LCOA_{tech}_2020'] > p_ref_ls[ip_ref])                     
                 _map_range_thr_m1 =\
                     (data_mtx[f'LCOA_{tech}_2030'] > p_ref_ls[ip_ref])
                 _map_range_thr_1 =\
                     (data_mtx[f'LCOA_{tech}_{year}'] <= p_ref_ls[ip_ref])
                 _map_range_thr =\
                     ((_map_range_thr_m2 & _map_range_thr_m1) & (_map_range_thr_1))                       
                
            data_mtx[f'ammonia-bthr_{tech}_{year}_{ip_ref}'][\
                ~_map_range_thr] = np.nan
            data_mtx[f'LCOA-bthr_{tech}_{year}_{ip_ref}'][\
                ~_map_range_thr] = np.nan           

            # convert to dataframe
            var = f'ammonia-bthr_{tech}_{year}_{ip_ref}'
            data_raster[var] =\
                data_raster['nitrogen']
            data_raster[var].values=\
                data_mtx[var]                    
            rds = data_raster[var].squeeze().drop("spatial_ref").drop("band")
            rds.name = var
            _df = rds.to_dataframe().reset_index()
            
            data_df[var] = _df[df_nonan.ref==df_nonan.ref][var]

        # case where all data are above the threshold
        _map_range_thr_m2 =\
            (data_mtx[f'LCOA_{tech}_2020'] > p_ref_ls[ip_ref])                     
        _map_range_thr_m1 =\
            (data_mtx[f'LCOA_{tech}_2030'] > p_ref_ls[ip_ref])
        _map_range_thr_1 =\
            (data_mtx[f'LCOA_{tech}_2050'] > p_ref_ls[ip_ref])
        _map_range_thr =\
            ((_map_range_thr_m2 & _map_range_thr_m1) & (_map_range_thr_1)) 
                                 
        data_mtx[f'ammonia-athr_{tech}_{ip_ref}'][\
            ~_map_range_thr] = np.nan
        data_mtx[f'LCOA-athr_{tech}_{ip_ref}'][\
            ~_map_range_thr] = np.nan               
            
        # convert to dataframe
        var = f'ammonia-athr_{tech}_{ip_ref}'
        data_raster[var] =\
            data_raster['nitrogen']
        data_raster[var].values=\
            data_mtx[var]                    
        rds = data_raster[var].squeeze().drop("spatial_ref").drop("band")
        rds.name = var
        _df = rds.to_dataframe().reset_index()
        
        data_df[var] = _df[df_nonan.ref==df_nonan.ref][var]                

#%%

print('*** create .csv')
data_df['country'] = country_df['country'].values
df_input = pd.read_csv('../input_data/data_csv/data_country.csv')
data_df['ammonia'] = df_input['nitrogen_current'].values*17/14

path_out = f'./output/combination-{system}/'
try:
    os.makedirs(path_out)
except OSError:
    pass

data_df.to_csv(path_out+'combination_ammonia.csv')

#%% aggregate at country scale

df = data_df.copy()
col_ls = [col for col in df.columns.tolist()\
          if (('bthr' in col) or ('athr' in col))]

country_ls = np.sort(df.country.drop_duplicates().dropna().tolist())
df_country = pd.DataFrame()

print('*** aggregation at country level')
for c in country_ls:
    
    map_c = (df.country == c)
    
    # total demand 
    df_country.loc[c, 'ammonia_tot'] = df.loc[map_c, 'ammonia'].sum()
    
    df_country.loc[c, 'ammonia_tot'] =\
        df.loc[map_c, 'ammonia'].sum()
    
    # demand without water scarcity
    df_country.loc[c, 'ammonia_tot'] =\
        df.loc[map_c, 'ammonia'].sum()
    
    # aggregate demand split by LCOA to country level
    for column in col_ls:
        
        df_country.loc[c, column] = df.loc[map_c, column].sum()

df_country.index.name = 'country'
df_country.to_csv(path_out+'combination_ammonia-country.csv', index=True)