#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 10:44:25 2023

    Script to plot the global LCOA distribution at global scale.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

# select the system: 
# (i)  agrivolt: supply of electricity from solar panels
# (ii) grid: connected to the grid

systems_ls = ['grid', 'agrivolt']

techs_ls = ['EHB', 'ENR']
years_ls = [2020, 2030, 2050]
figsize = (10, 3)
xlim = [250, 3.25e3]
ylim = [0, 0.0076]
colors = {
    2020:'#c73818',
    2030:'#1938b3',
    2050:'#039130'
    }
        
# ===================== 简化版：只画密度曲线（无箭头/标注） =====================
import matplotlib.pyplot as plt
import rioxarray as rxr
import numpy as np
from scipy.stats import gaussian_kde
import os

# 1. 基础设置（和你的脚本兼容）
systems_ls = ['grid', 'agrivolt']
techs_ls = ['EHB', 'ENR']  # 两个技术都会生成图
years_ls = [2020, 2030, 2050]
figsize = (10, 6)
xlim = [250, 3.25e3]
ylim = [0, 0.0076]

# 颜色设置：和你原来的/文献一致
colors = {
    2020: '#c73818',    # 红
    2030: '#1938b3',    # 蓝
    2050: '#039130'     # 绿
}
fill_alpha = 0.3  # 半透明填充，和文献的渐变效果匹配

# 2. 输出路径
path_out = './output/lcoa_hist_combined/'
os.makedirs(path_out, exist_ok=True)

# 3. 循环生成每个技术的图（无额外标注）
for tech in techs_ls:
    plt.figure(figsize=figsize)
    ax = plt.gca()
    
    # 读取两个系统的数据，全部画在同一张图
    for system in systems_ls:
        for year in years_ls:
            # 读取tif文件
            tif_path = f'../calculation/output/cost-{system}/global_tif/LCOA_{tech}_EUR_t-{year}.tif'
            da = rxr.open_rasterio(tif_path).squeeze()
            data = da.values[np.isfinite(da.values)]
            
            # 计算密度分布
            kde = gaussian_kde(data)
            x_vals = np.linspace(xlim[0], xlim[1], 1000)
            y_vals = kde(x_vals)
            
            # 绘制密度曲线 + 半透明填充
            ax.plot(x_vals, y_vals, color=colors[year], linewidth=2)
            ax.fill_between(x_vals, y_vals, color=colors[year], alpha=fill_alpha)
            
            # 绘制平均值的垂直虚线（和文献里的短虚线一致）
            mean_val = np.mean(data)
            ax.axvline(x=mean_val, color=colors[year], linestyle='--', linewidth=3)

    # 只保留基础的坐标轴和技术名称，去掉额外标注
    ax.set_title(tech, fontsize=20)
    ax.set_xlabel("Price of ammonia (€ t⁻¹ of NH₃)", fontsize=18, labelpad=15)
    ax.set_ylabel("Density (-)", fontsize=18, labelpad=15)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.tick_params(axis='both', labelsize=16)

    plt.tight_layout()
    
    # 保存图片
    plt.savefig(f"{path_out}/LCOA_{tech}_simple.tiff", dpi=300, bbox_inches='tight')
    plt.close()

print(f"✅ 简化版图片已生成，保存在：{path_out}")
        