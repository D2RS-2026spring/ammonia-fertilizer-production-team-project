#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 14:44:54 2023

    Script to extract the data from .tif and convert into dataframes.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

var_ls = [
        'nitrogen_current',
        'solar_potential',
        'solar_to_peak',
        'area_harvest'
        ]

filename_dict = {
    'area_harvest'    :    'area-2020-reproj.tif',
    'nitrogen_current':    'current_syn_nitrogen-2020-reproj.tif',
    'solar_potential' :    'GHI-resampled-reproj.tif',
    'solar_to_peak'   :    'PVOUT-resampled-reproj.tif'
    }

path_out = './data_csv/'

import pandas as pd
import rioxarray as rxr
import os

try:
    os.makedirs(path_out)
except OSError:
    pass
    
data_tif = {}
data_df = {}
df_out = pd.DataFrame()

# reference database from nan exclusion
path_in = './data_tif/'
tif_nonan = rxr.open_rasterio(path_in+filename_dict['area_harvest'],\
                              masked=True)

for var in var_ls:

    data_tif[var] = rxr.open_rasterio(path_in+filename_dict[var], masked=True)
    rds = data_tif[var].squeeze().drop("spatial_ref").drop("band")
    rds.name = var
    data_df[var] = rds.to_dataframe().reset_index()
    
    if var == var_ls[0]:
        print('reference file:', filename_dict[var])
        map_nonan = data_df[var][var] == data_df[var][var] 
        
        df_out['x'] = data_df[var][map_nonan].x.values
        df_out['y'] = data_df[var][map_nonan].y.values

    df_out[var] = data_df[var][map_nonan][var].values

    # # convert input area from ha to km2
    # if var == 'area_km2':
    #     df_out[var] =  df_out[var]/100
    
df_out.to_csv(path_out+'data_nitrogen.csv', index=False)