#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 17:31:38 2023

    Script to check co-registered data.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import rioxarray as rxr
import matplotlib.pyplot as plt
import numpy as np

var_ls = [
        'nitrogen_current',
        'solar_potential',
        'solar_to_peak',
        'area_harvest'
        ]

#%%
data = {}
for variable in var_ls:
    
    if variable == 'nitrogen_current':
        
        path = './data_tif/' 
        filename = 'current_syn_nitrogen-2020.tif'
        variable_descr = 'total N - present production' 
    
    elif variable == 'solar_potential':
        
        path = './data_tif/'        
        filename = 'GHI-resampled.tif'
        variable_descr = 'solar irradiation'    

    elif variable == 'area_harvest':
        
        path = './data_tif/'
        filename = 'area-2020.tif'
        variable_descr = 'harvested area'   

    elif variable == 'solar_to_peak':
        
        path = './data_tif/'      
        filename = 'PVOUT-resampled.tif'
        variable_descr = 'solar capacity factor'    
    
    name = filename.split('.')[0]
    input_filename = f'./data_tif/{name}-reproj.tif'
    data[variable] = rxr.open_rasterio(input_filename, masked=True)
    
    plt.figure()
    data[variable].values[data[variable].values<=0] = np.nan
    plt.imshow(data[variable][0,:,:].values)
    plt.title(variable)
    plt.savefig(variable+'.png', dpi=500)

#%%    

for variable in var_ls:
    
    print(f'### variable {variable}:')
    values_nonan = data[variable].values[
        data[variable].values==data[variable].values]
    
    scale = 1e9
    print(f'tot - e{int(np.log10(scale))}:', round(values_nonan.sum()/scale,3))
    