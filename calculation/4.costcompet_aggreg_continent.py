#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 11:38:13 2023

    Script to aggregate data to a continental scale.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

# select the system: 
# (i)  agrivolt: supply of electricity from solar panels
# (ii) grid: connected to the grid

system = 'agrivolt'

import pandas as pd

path_in = './input/'
filename = 'continent_list.xlsx'
file_continent = pd.read_excel(path_in+filename, 
                               index_col='country')
file_continent.rename(index={"C√¥te d'Ivoire": "Cote d'Ivoire"}, inplace=True)

path_in = f'./output/combination-{system}/'
path_out = path_in
filename = 'combination_ammonia-country.csv'
filename_out = filename.replace('country', f'continent2-{system}').replace('csv', 'xlsx')
file_path = r"C:\Users\hui\ammonia_decentralized\calculation\output\combination-grid\combination_ammonia-country.csv"
file_data = pd.read_csv(file_path, index_col=0)

file_data.rename(index={"Côte d'Ivoire": "Cote d'Ivoire"}, inplace=True)

for c in file_data.index.tolist():
    
    file_data.loc[c, 'continent'] = file_continent.loc[c, 'continent']
    
file_data.rename(index={"Cote d'Ivoire":"Côte d'Ivoire"}, inplace=True)

continent_ls = file_data.continent.drop_duplicates().tolist()

data_continent = pd.DataFrame()

cols_ls = file_data.columns.tolist()
cols_ls.remove('continent')

for continent in continent_ls:
    for column in cols_ls:
        
        map_index = file_data[file_data.continent == continent].index
        
        data_continent.loc[continent, column] =\
            file_data.loc[map_index, column].sum()/1e6
            
data_continent.to_excel(path_out+filename_out)
