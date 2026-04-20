#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 08:36:46 2023

    Plot results of Sobol index in the form of matrix

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
import os

path_out = './output/uncertainty-2/'
try:
	os.makedirs(path_out)
except OSError:
	pass


plt.rcParams.update({'font.size': 18})

years_ls = [2020, 2030, 2050]

df_dict = {}
for metric in ['LCOE_PV', 'LCOA_ENR', 'LCOA_EHB']:
    for year in years_ls:
        for stat in ['mean', 'median', 'std']:
            
            key = f'{metric}_{year}-{stat}'
            df_dict[key] = pd.read_csv('../calculation/output/sensitivity/'+\
                                       f'sobol-{key}.csv', index_col=0)

indices_dict = {}
indices_dict['LCOE_PV'] =\
    [idx for idx in df_dict[key].index.tolist() if (('ENR' not in idx) and 
                                                    'eHB' not in idx)]
indices_dict['LCOA_ENR'] =\
    [idx for idx in df_dict[key].index.tolist() if 'ENR_' not in idx]

indices_dict['LCOA_EHB'] =\
    [idx for idx in df_dict[key].index.tolist() if 'eHB_' not in idx]    

#%%            

S_dict = {}
stat = 'median'
for metric in ['LCOE_PV', 'LCOA_ENR', 'LCOA_EHB']:
            
    if metric == 'LCOA_ENR':
        _indices = [idx for idx in df_dict[key].index.tolist() if 
                    'eHB' not in idx]
        
    elif metric == 'LCOA_EHB':
        _indices = [idx for idx in df_dict[key].index.tolist() if 
                    'ENR' not in idx]

    elif metric == 'LCOE_PV':
        _indices = [idx for idx in df_dict[key].index.tolist() if 
                    (('ENR' not in idx) and ('eHB' not in idx))]		
                          
    df = pd.DataFrame(index = _indices)
    for year in years_ls:
        
        key = f'{metric}_{year}-{stat}'
        
        # df.loc[_indices, f'S1-{year}'] = df_dict[key].loc[_indices, 'S1']
        
        # max_value = df_dict[key].loc[_indices, 'ST'].max()
        # df.loc[_indices, f'ST-{year}'] =\
        #     df_dict[key].loc[_indices, 'ST']/max_value*100
        
        df.loc[_indices, f'ST-{year}'] = df_dict[key].loc[_indices, 'ST']        

    for order in ['ST']:
        
        S = df.loc[_indices, [f'{order}-{y}' for y in years_ls]]

        X = np.arange(S.shape[0])[:,np.newaxis]@np.ones([1, S.shape[1]])
        Y = np.ones(S.shape[0])[:,np.newaxis]@np.arange(S.shape[1])[np.newaxis,:]
    
        metrics = S.columns.tolist()
        indices = S.index.tolist()
        print(metric, _indices)
        print('\nS min', S.values.min(), 'S max', S.values.max())
        
        original_cmap = plt.cm.Blues 
        # Set the color range you want to extract
        start_color = 0.1  # Adjust based on your requirements
        end_color = 1    # Adjust based on your requirements
        
        # Create a new colormap with the desired color range
        colors = original_cmap(np.linspace(start_color, end_color, 10))
        new_cmap = ListedColormap(colors)

        plt.figure(figsize=(10, 2.5))
        plt.scatter(x=X, y=Y, marker='s', s=1.5e3, alpha= 0.9,\
                    c=S.loc[indices,metrics].values,
                    cmap=new_cmap, vmin=0, vmax=1)
        plt.colorbar(
            aspect=5
            )
        plt.ylim([-0.5, 2.5])
        plt.xlim([-0.5, 10])
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        plt.xticks(np.arange(len(indices)), indices, rotation = 90)
        plt.yticks(np.arange(len(metrics)), metrics)
        
        namefile = order + ' - ' + metric + ' - ' + stat
		
        plt.title(namefile)
		
        plt.savefig(path_out+f'{namefile}.tiff', 
				  dpi=500,
		          bbox_inches='tight',
		          transparent=True)
		
