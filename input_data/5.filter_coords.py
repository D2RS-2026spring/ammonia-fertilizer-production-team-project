#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 15:47:57 2023

Script to check the nitrogen and ammonia demand at too high lats and too low lats.

Modified: 优化纬度筛选范围，修正数据统计逻辑，提升数据准确性
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

# ====================== 这里是你修改的数据逻辑 ======================
# 原范围：>60°N
# 修改后：>55°N（更符合真实高纬度农业区范围）
mask_values_1 = (Y_mtx < -180)
mask_values_2 = (Y_mtx > 55)

values_extr_lats = values[Y_mtx > 55]

# 增加非空判断，避免无效数据影响统计
valid_values = values_extr_lats[np.isfinite(values_extr_lats)]
NH3tots = valid_values.sum() * 17 / 14

# 增加输出，方便查看结果
print(f"高纬度区域 NH3 总需求量: {NH3tots:.2f} 吨")
# ==================================================================
