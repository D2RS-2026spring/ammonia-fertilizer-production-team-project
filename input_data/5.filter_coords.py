#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 15:47:57 2023

    Script to check the nitorgen and ammonia demand at too high lats and too
    low lats.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import rioxarray as rxr
import numpy as np
import rasterio

data = {}
variable = 'nitrogen_current'
        
path = './data_tif/' 
filename = 'current_syn_nitrogen-2020.tif'
variable_descr = 'total N - present production' 

name = filename.split('.')[0]
input_filename = f'./data_tif/{name}-reproj.tif'
data[variable] = rxr.open_rasterio(input_filename, masked=True)
values = data[variable].values[0,:,:]

X_arr = np.linspace(-180, 180, 4320)
X_mtx = np.ones([2160, 1])@X_arr[np.newaxis,:]

Y_arr = np.linspace( -90,  90, 2160)
Y_mtx = Y_arr[:,np.newaxis]@np.ones([1, 4320])

#%%

mask_values_1 = (Y_mtx<-180)
mask_values_2 = (Y_mtx>60)

values_extr_lats = values[Y_mtx>60]

NH3tots = values_extr_lats[values_extr_lats==values_extr_lats].sum()*17/14
