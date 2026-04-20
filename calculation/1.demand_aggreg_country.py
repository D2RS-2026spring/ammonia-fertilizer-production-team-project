#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 18:02:54 2023

    Script to aggregate data at pixel-level to world- and country-level.
    
@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import rioxarray as rxr
import numpy as np
import pandas as pd
import os

path_out = './output/data_aggregated/'
try:
    os.makedirs(path_out)
except:
    OSError
    
path = '../input_data/data_csv/'  
filename = 'data_country.csv'
data_raw = pd.read_csv(path+filename).drop(columns=['Unnamed: 0'])

# collect data for processing
data = pd.DataFrame()
data[['lon_deg', 'lat_deg']] = data_raw[['x', 'y']]
data['nitrogen_t_year'] = data_raw['nitrogen_current']
data['area_harvest_km2'] = data_raw['area_harvest']/100
data['solar_irradiation_kWh_d_m2'] = data_raw['solar_potential']
data['solar_to_peak_kWh_kWp'] = data_raw['solar_to_peak']
data['country'] = data_raw['country']

country_ls = np.sort(data.country.drop_duplicates().dropna().tolist()).tolist()

data_country = pd.DataFrame(index=country_ls)

for country in country_ls:
    
    if country_ls.index(country)%10 == 0:
        print(country_ls.index(country),'/', len(country_ls))
        
    map_country = (data.country==country)
    
    for var in ['nitrogen_t_year', 'area_harvest_km2']:
        
        data_country.loc[country, var] = data.loc[map_country, var].sum()
        
data_country.to_csv(path_out+'country_level.csv')

df_world = pd.DataFrame()
df_world.loc['world', 'nitrogen_t_year'] = data['nitrogen_t_year'] .sum()
df_world.to_csv(path_out+'world_level.csv', index=True)