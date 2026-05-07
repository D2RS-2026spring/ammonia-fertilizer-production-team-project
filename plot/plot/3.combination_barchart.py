#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:24:36 2023

    Script to plot bar chart for countries with greatest demand.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

# select the system: 
# (i)  agrivolt: supply of electricity from solar panels
# (ii) grid: connected to the grid

system = 'agrivolt'

print('\n# SYSTEM:', system, '\n')

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.pyplot as mpl
mpl.rcParams['font.size'] = 20

# input data
path_in = f'../calculation/output/combination-{system}/'
filename = 'combination_ammonia-country.csv'
df_country = pd.read_csv(path_in+filename, index_col='country')

path_out = f'./output/lcoa_country-{system}/'
try:
    os.makedirs(path_out)
except OSError:
    pass
        
# conversion to Mt/y of ammonia
df_country = df_country/1e6

color_dict = {}
edgecolor_dict = {}
hatch_dict = {}

for col in df_country.columns.tolist():
    if (('2020' in col) and ('bthr' in col)):
        color_dict[col] = '#c73818' # 'r'
    elif (('2030' in col) and ('bthr' in col)):
        color_dict[col] = '#1938b3' #'b'
    elif (('2050' in col) and ('bthr' in col)):
        color_dict[col] = '#039130' #'g'
    elif 'athr' in col:
        color_dict[col] = 'yellow'

for col in color_dict:
    edgecolor_dict[col] = 'None'
    hatch_dict[col] = 'None'  

NH3_prices = pd.read_excel('../calculation/input/ammonia_prices.xlsx',
                           engine='openpyxl', index_col='date')
# U.S. dollars per metric ton
p_ref_ls = NH3_prices.price.values.tolist()
years_ls = [2020, 2030, 2050]

#%%

countries_ref =\
    df_country.sort_values(by='ammonia_tot', ascending=False).index.tolist()    

Nc = 22
N_A = 3

for panel in ['A', 'B', 'C']:
    print('### panel', panel)
        
    if panel == 'A':
        c_ls = countries_ref[:N_A]
        c_tx = countries_ref[:Nc]
        figsize = (8,3)
        width = 0.6
        xlim = [-.5, Nc+.5]
        # dx_ticks = 0.2
        # xlim = [-1+dx_ticks+.4, Nc+dx_ticks-.4]
        ylim = [0, 31]

    elif panel == 'B':
        c_ls = countries_ref[N_A:Nc+N_A]
        c_tx = c_ls
        figsize = (8,3)
        width = 0.6
        xlim = [-.5, Nc-1+.5]
        # dx_ticks = 0.2
        # xlim = [-1+dx_ticks+.4, Nc+dx_ticks-.4]
        ylim = [0, 10]
        
    elif panel == 'C':
        c_oths = countries_ref[Nc+N_A:]
        c_ls = ['other countries']
        c_tx = c_ls
        df_country.loc['other countries',:] =\
            df_country.loc[c_oths,:].sum(axis=0)
        figsize = (8/Nc,3)
        width = 0.6
        xlim = [-.5, .5]
        # dx_ticks = 0.2
        # xlim = [-0.15, 0.15]
        ylim = [0, 20]
    
    df_out = pd.DataFrame(index = c_ls)
    
    plt_dict = {
        'width': width,
        'figsize': figsize,
        'alpha':0.9,
        'stacked':True,
        'legend':False
        }        
    
    # loop over reference ammonia price thresholds
    for ip_ref in range(len(p_ref_ls)):
        
        # loop over technologies involved
        for tech in ['ENR', 'EHB']:
            
            dem = 'ammonia'
            cols_stack_1 = []
            colors_ls_1 = []
            for col in df_country.columns.tolist()[::-1]:
                if (dem in col) and ('bthr' in col) and (tech in col) and\
                    (col.split('_')[-1]==str(ip_ref)):
                    cols_stack_1.append(col)     
                    colors_ls_1.append(color_dict[col])
            edgecolors_ls_1 = [edgecolor_dict[col] for col in cols_stack_1]
            hatch_ls_1 = [hatch_dict[col] for col in cols_stack_1]       
            
            # add the stack with demand which is never competitive
            col = f'ammonia-athr_{tech}_{ip_ref}'
            cols_stack_1.append(col)
            colors_ls_1.append(color_dict[col])
            edgecolors_ls_1.append(edgecolor_dict[col])
            hatch_ls_1.append(hatch_dict[col])         
            
            plt.figure()       
            
            plt_dict['ax'] = plt.gca()
            plt_dict['color'] = colors_ls_1       
            plt_dict['edgecolor'] = edgecolors_ls_1     
            
            df_country.index.name = ''
    
            df_country.loc[c_ls, cols_stack_1].plot.bar(
                **plt_dict
                )         
            
            df_out.loc[c_ls, cols_stack_1] = df_country.loc[c_ls, cols_stack_1]     
           
            if False:
                ax = plt.gca()
                ## SCATTER PLOT
                cols_scatter = ['ammonia_tot']  
                dx_position1 = 0
                scatter_colors = {
                    'ammonia_tot': 'k',
                    }
                for col in cols_scatter:
                    dem_x = col.split('-')[-1]
                    x_pos = np.arange(len(c_ls)) + dx_position1
                    if panel == 'C':
                        x_pos = np.arange(len(c_ls))
                       
                    ax.scatter(x_pos, df_country.loc[c_ls, col].values,
                                c=scatter_colors[col], 
                                marker='x')
    
            plt.xlim(xlim)     
            plt.ylim(ylim)
            
            plt.ylabel('NH$_{3}$ demand (Mt/y)')
            plt.savefig(path_out+f'{ip_ref}_{dem}_{tech}-{panel}.tiff',
                        dpi=500,
                        bbox_inches='tight',
                        transparent=True)
        
        # df_out.T.to_csv(path_out+f'df_out_NH3-{panel}.csv', index=True)
