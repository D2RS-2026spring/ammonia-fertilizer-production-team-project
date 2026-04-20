#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 11:34:43 2023

    Script to chekc the cost breakdown.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# select the system: 
# (i) agrivolt: supply of electricity from solar panels
# (ii) grid: connected to the grid
system = 'grid'

path_in = f'../calculation/output/cost-{system}/breakdown/'
tech_ls = ['eHB', 'ENR', 'PV']

data = {}
df_f = {}
df_v = {}
df = {}

for tech in tech_ls:
    
    json_file_path = path_in+f'{tech}_params.json'
    
    with open(json_file_path, 'r') as file:
        data[tech] = json.load(file)
    
    df_f[tech] = pd.DataFrame()
    df_v[tech] = pd.DataFrame()

year_ls = [2020, 2030, 2050]

from matplotlib import colors as mcolors
c_list = list(dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS).values())[103::5]

path_out = f'./output/cost_breakdown-{system}/'
try:    
    os.makedirs(path_out)    
except OSError:    
    pass

#%% eHB cost

tech = 'eHB'

# FIXED COST
var_ls = [
    'capex EL', 'capex HB', 'ASU cost', 'OandM cost', 'storage cost'   
    ]
N0 = len(var_ls)
c_dict = {}
for year in year_ls:
    for var in var_ls:
        
        df_f[tech].loc[var, year] = data[tech][str(year)]['out'][var]
        c_dict[var] = c_list[var_ls.index(var)]
        
    print(f"total cost - {year} - {data[tech][str(year)]['out']['fixed cost']:.2f}")
    print(f"sum cost - {df_f[tech][year].sum():.2f}")

# VARIABLE COST
var_ls = [
    'varc - electrolyzer', 'varc - HB', 'varc - ASU',
    ]
for year in year_ls:
    for var in var_ls:
        
        df_v[tech].loc[var, year] = data[tech][str(year)]['out'][var]
        c_dict[var] = c_list[N0+var_ls.index(var)]
        
    print(f"total cost - {year} - {data[tech][str(year)]['out']['variable cost']:.2f}")
    print(f"sum cost - {df_v[tech][year].sum():.2f}")

df[tech] = pd.concat([df_f[tech], df_v[tech]], axis=0)
    
plt_dict = {
    # 'title': f'fixed costs - {tech}',
    'stacked': True,
    'width':0.4,
    'position':0.5,
    'figsize':(3,5),
    'color':c_dict,
    'ylabel':'EUR/t$_{NH3}$'    
    }

plt.figure()
df_f[tech].T.plot.bar(**plt_dict)
plt.ylim([0, 500])
plt.legend(loc=(1.1,0.1))
filename = f'{tech}-fixed_cost.png'
plt.savefig(path_out+filename,
            dpi=800,
            bbox_inches='tight',
            transparent=True)

# plt_dict['title'] = 'variable costs'
plt.figure()
df_v[tech].T.plot.bar(**plt_dict)
plt.ylim([0, 2.5e3])
plt.legend(loc=(1.1,0.1))
filename = f'{tech}-variable_cost.png'
plt.savefig(path_out+filename,
            dpi=800,
            bbox_inches='tight',
            transparent=True)

# plt_dict['title'] = 'all costs'
plt.figure()
df[tech].T.plot.bar(**plt_dict)
plt.ylim([0, 3e3])
plt.legend(loc=(1.1,0.1))

filename = f'{tech}-total_cost.png'
plt.savefig(path_out+filename,
            dpi=800,
            bbox_inches='tight',
            transparent=True)

#%% ENR cost

tech = 'ENR'

# FIXED COST
var_ls = [
    'capex', 'ASU cost', 'OandM cost'
    ]
N0 = len(var_ls)
c_dict = {}
for year in year_ls:
    for var in var_ls:
        
        df_f[tech].loc[var, year] = data[tech][str(year)]['out'][var]
        c_dict[var] = c_list[var_ls.index(var)]
        
    print(f"total cost - {year} - {data[tech][str(year)]['out']['fixed cost']:.2f}")
    print(f"sum cost - {df_f[tech][year].sum():.2f}")

# VARIABLE COST
var_ls = [
    'varc - ENR', 'varc - ASU'
    ]
for year in year_ls:
    for var in var_ls:
        
        df_v[tech].loc[var, year] = data[tech][str(year)]['out'][var]
        c_dict[var] = c_list[N0+var_ls.index(var)]        
        
    print(f"total cost - {year} - {data[tech][str(year)]['out']['variable cost']:.2f}")
    print(f"sum cost - {df_v[tech][year].sum():.2f}")

df[tech] = pd.concat([df_f[tech], df_v[tech]], axis=0)
    
plt_dict = {
    # 'title': f'fixed costs - {tech}',
    'stacked': True,
    'width':0.4,
    'position':0.5,
    'figsize':(3,5),
    'color':c_dict,
    'ylabel':'EUR/t$_{NH3}$'
    }

plt.figure()
df_f[tech].T.plot.bar(**plt_dict)
plt.ylim([0, 500])
plt.legend(loc=(1.1,0.1))
filename = f'{tech}-fixed_cost.png'
plt.savefig(path_out+filename,
            dpi=800,
            bbox_inches='tight',
            transparent=True)

# plt_dict['title'] = 'variable costs'
plt.figure()
df_v[tech].T.plot.bar(**plt_dict)
plt.ylim([0, 2.5e3])
plt.legend(loc=(1.1,0.1))
filename = f'{tech}-variable_cost.png'
plt.savefig(path_out+filename,
            dpi=800,
            bbox_inches='tight',
            transparent=True)

# plt_dict['title'] = 'all costs'
plt.figure()
df[tech].T.plot.bar(**plt_dict)
plt.ylim([0, 3e3])
plt.legend(loc=(1.1,0.1))

filename = f'{tech}-total_cost.png'
plt.savefig(path_out+filename,
            dpi=800,
            bbox_inches='tight',
            transparent=True)
