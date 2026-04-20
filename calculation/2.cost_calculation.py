#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 09:10:24 2023

    Script to compute the local cost of electricity from solar panels (LCOE)
    and derive the cost of ammonia production per technology.

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

# select the system: 
# (i)  agrivolt: supply of electricity from solar panels
# (ii) grid: connected to the grid

system = 'agrivolt'

print('\n# SYSTEM:', system)

import os
import numpy as np
import pandas as pd
import rioxarray as rxr
import json

#%%
# input data
paths = {
    'area': '../input_data/data_tif/',
    'GHI': '../input_data/data_tif/',
    'nitrogen':'../input_data/data_tif/',
    'PVOUT':'../input_data/data_tif/',
    }

filenames = {
    'area':'area-2020-reproj.tif', 
    'GHI':'GHI-resampled-reproj.tif', 
    'nitrogen':'current_syn_nitrogen-2020-reproj.tif',
    'PVOUT':'PVOUT-resampled-reproj.tif'
    }

data_mtx = {}
data_raster = {}

for var in filenames.keys():
    
    data_raster[var] = rxr.open_rasterio(
        paths[var]+filenames[var], masked=True)
    
    data_mtx[var] = data_raster[var].values
    
path_out = f'./output/cost-{system}/global_tif/'
path_out_c = f'./output/cost-{system}/country_statistics/'
path_out_b = f'./output/cost-{system}/breakdown/'
for path in [path_out, path_out_b, path_out_c]:
    try:
        os.makedirs(path)
    except OSError:
        pass    

#%% input data

path = './input/'
filename = 'parameters_cost.xlsx'
# dictionary with all the data
data_techs_excel = pd.read_excel(path+filename, engine='openpyxl', 
                                 sheet_name=None)
GEN = data_techs_excel['general'].set_index('parameter')
PV = data_techs_excel['PV'].set_index('parameter')
ENR = data_techs_excel['ENR'].set_index('parameter')
eHB = data_techs_excel['eHB'].set_index('parameter')

years_ls = [2020, 2030, 2050]
hours_y = 8760
days_y = 365
hours_d = 24

# PV input data
input_param_ls = [
    'lifetime',
    'degradation_rate',
    'capex',
    'OandM_expenses-fixed',
    'panel_to_soil_surf',
    'conversion_efficiency'
    ]
    
PV_params = {}
PV_params['SYSTEM'] = system
for year in years_ls:  
    PV_params[year] = {}
    PV_params[year]['out'] = {}
    for param in input_param_ls:
        PV_params[year][param] =\
            PV.loc[PV.year==year].loc[param,'value'].item()

input_param_ls = [
    'enthalphy reaction',
    'faradaic efficiency',
    'theoretical voltage',
    'overpotential',
    'capex electrolyzer',
    'efficiency electrolyzer',        
    'OandM capex fraction',
    'ASU capex fraction',
    'ASU energy consumption',
    'capacity factor',
    'lifetime'
    ]

ENR_params = {}
ENR_params['SYSTEM'] = system
for year in years_ls:  
    ENR_params[year] = {}
    ENR_params[year]['out'] = {}
    for param in input_param_ls:
        ENR_params[year][param] =\
            ENR.loc[ENR.year==year].loc[param,'value'].item()
            
input_param_ls = [
    'capex electrolyzer',
    'efficiency electrolyzer',
    'capex Haber Bosch normal.',  
    'energy required HB plant',
    'storage fraction',
    'OandM capex fraction',
    'ASU capex fraction',
    'ASU energy consumption',
    'capacity factor',
    'lifetime',
    ]

eHB_params = {}
eHB_params['SYSTEM'] = system
for year in years_ls:  
    eHB_params[year] = {}
    eHB_params[year]['out'] = {}
    for param in input_param_ls:
        eHB_params[year][param] =\
            eHB.loc[eHB.year==year].loc[param,'value'].item() 

#%% create rasterio database for export
LevCost, LevCost_raster = {}, {}
metrics_ls = ['LCOE_PV', 'LCOA_ENR', 'LCOA_EHB']
    
for metric in metrics_ls:    
    LevCost[metric] = {}
    LevCost_raster[metric] = {}
    for year in years_ls:
        LevCost_raster[metric][year] = rxr.open_rasterio(
                    paths['nitrogen']+filenames['nitrogen'],\
                    masked=True).copy() 

#%%
conv_USD_EUR = GEN[GEN['year']==2022].loc['usd_to_eur', 'value']
LHV_H2 = GEN.loc['LHV H2', 'value']
LHV_NH3 = GEN.loc['LHV NH3', 'value']
m_ratio_NH3toH2 = GEN.loc['mass ratio', 'value']

# capacity factor (-)
data_mtx['capacity_factor'] = data_mtx['PVOUT']/hours_d

############################################################################### 
# LCOE CALCULATION
############################################################################### 
for year in years_ls: 
    
    print('\n*** YEAR', year)    
    
    # conversion efficiency irradiation to power (-)
    eta = PV_params[year]['conversion_efficiency']
    # panel soil area ratio (-)
    gamma = PV_params[year]['panel_to_soil_surf']
    
    # yearly production - kWh/d/m2 to TWh/y/km2
    PV_params[year]['out']['solar_prod_TWh_km2'] =\
        data_mtx['GHI']*days_y*1e-3*eta*gamma
    # yearly solar irradiation captured - kWh/d/m2 to TWh/y/km2
    PV_params[year]['out']['solar_irr_TWh_km2'] =\
        data_mtx['GHI']*days_y*1e-3*gamma
    # CF - kW/kWp
    PV_params[year]['out']['solar_capacity_factor'] =\
        data_mtx['capacity_factor']
    # land - km2
    PV_params[year]['out']['area_km2'] = data_mtx['area']/100
    
    # solar energy production - MWh/y
    PV_params[year]['out']['potential_el'] =\
        PV_params[year]['out']['solar_prod_TWh_km2']*1e6*\
        PV_params[year]['out']['area_km2']
    
    # capacity installed - MW
    PV_params[year]['out']['capacity_MW'] =\
        PV_params[year]['out']['potential_el']/hours_y/\
        data_mtx['capacity_factor']
    
    # lifetime - y
    lifetime_PV = int(PV_params[year]['lifetime'])
    lifetime_arr = np.arange(1, lifetime_PV+1)
    # degradation rate [-]
    d = PV_params[year]['degradation_rate']
    # discount rate [-]
    r = GEN.loc[GEN.year==year].loc['discount_rate','value'].item()
    
    # capex - EUR/kW
    capex = PV_params[year]['capex']*conv_USD_EUR
    
    print('capex -', year, round(capex,1))
    
    # O&M fixed - EUR/kW/y
    OandM_fixed = PV_params[year]['OandM_expenses-fixed']*conv_USD_EUR
    
    print('OandM_fixed -', year, round(OandM_fixed))
        
    # TLCC Fixed = Total Life Cycle Cost [EUR/kW]
    TLCC_f = capex + sum([OandM_fixed/(1+r)**t for t in lifetime_arr])
    
    # numerator of LCOE - total lyfe cycle costing [EUR/kW]
    LCOE_num = TLCC_f
    # denominator LCOE - energy produced divided by disc. rate LCOE [kWh/kW]
    LCOE_den = sum([(PV_params[year]['out']['potential_el']/\
                      PV_params[year]['out']['capacity_MW']*(1-d)**t)/(1+r)**t\
                      for t in lifetime_arr])     
    
    # levelized cost of electricity [EUR/MWh]    
    LevCost['LCOE_PV'][year] = LCOE_num/LCOE_den*1e3   

    PV_params[year]['out']['capex-fraction'] = capex/TLCC_f
    PV_params[year]['out']['OandM-fraction'] =\
        sum([OandM_fixed/(1+r)**t for t in lifetime_arr])/TLCC_f
    
    mtx = LevCost['LCOE_PV'][year][LevCost['LCOE_PV'][year]==\
                                   LevCost['LCOE_PV'][year]]
    print('LCOE EUR/MWh -', 
          'min',  round(mtx.min(),1),
          'mean', round(mtx.mean(),1),
          'max',  round(mtx.max(),1))
    
# pick the mean values of arrays
for year in years_ls:
    for key in PV_params[year]['out']:
        if type(PV_params[year]['out'][key]) == np.ndarray:
            
            map_nonan = ~np.isnan(PV_params[year]['out'][key])
            PV_params[year]['out'][key] =\
                PV_params[year]['out'][key][map_nonan].mean(dtype=float)

# save the data to a JSON file
with open(path_out_b+'PV_params.json', 'w') as json_file:
    json.dump(PV_params, json_file)    

#%%
############################################################################### 
# COST OF AMMONIA CALCULATION - ENR
###############################################################################   
            
for year in years_ls:

    print('\n*** YEAR', year)
    
    # total voltage = thermodynamic voltage + overpotential (V)
    ENR_params[year]['out']['total voltage'] =\
        ENR_params[year]['theoretical voltage'] +\
            ENR_params[year]['overpotential']
    
    # energy efficiency =\
    #     (faradaic efficiency)*(theoretical voltage)/(total voltage) (-)   
    ENR_params[year]['out']['energy efficiency'] =\
        ENR_params[year]['faradaic efficiency']*\
        ENR_params[year]['theoretical voltage']/\
            ENR_params[year]['out']['total voltage']
        
    # energy required (MWh/t_NH3)
    ENR_params[year]['out']['energy required'] =\
        ENR_params[year]['enthalphy reaction']/\
            ENR_params[year]['out']['energy efficiency']
    
    ## capex electrocatalysis (EUR/t_NH3)
    T = ENR_params[year]['lifetime'] 
    eta = ENR_params[year]['out']['energy efficiency']
    s = ENR_params[year]['out']['energy efficiency']
    
    if system == 'grid':
        cf = ENR_params[year]['capacity factor']
    elif system == 'agrivolt':
        cf = data_mtx['capacity_factor']
    else:
        raise OSError
    
    ENR_params[year]['out']['capacity factor'] = cf
    
    # convert capex electrolyser (EUR/kWel) into (EUR/t_Nh3) 
    conversion_coeff = T*cf*8760*eta/1000/LHV_NH3
    ENR_params[year]['out']['capex'] =\
        ENR_params[year]['capex electrolyzer']/conversion_coeff
        
    # operation and manteinance fixed cost (EUR/t_Nh3) 
    ENR_params[year]['out']['OandM cost'] =\
        ENR_params[year]['OandM capex fraction']*\
            ENR_params[year]['out']['capex']
    
    ENR_params[year]['out']['ASU cost'] =\
        ENR_params[year]['ASU capex fraction']*\
            ENR_params[year]['out']['capex']

    ENR_params[year]['out']['fixed cost'] =\
        ENR_params[year]['out']['capex']+\
            ENR_params[year]['out']['OandM cost']+\
                ENR_params[year]['out']['ASU cost'] 

    ENR_params[year]['out']['varc - ENR'] =\
        LevCost['LCOE_PV'][year]*ENR_params[year]['enthalphy reaction']/\
        ENR_params[year]['out']['energy efficiency']
        
    ENR_params[year]['out']['varc - ASU'] =\
        ENR_params[year]['ASU energy consumption']*LevCost['LCOE_PV'][year]        
        
    ENR_params[year]['out']['variable cost'] =\
        ENR_params[year]['out']['varc - ENR']+\
            ENR_params[year]['out']['varc - ASU']
    
    LevCost['LCOA_ENR'][year] = ENR_params[year]['out']['variable cost'] +\
        ENR_params[year]['out']['fixed cost']
    
    mtx = LevCost['LCOA_ENR'][year][LevCost['LCOA_ENR'][year]==\
                                   LevCost['LCOA_ENR'][year]]
        
    print('LCOA - ENR EUR/MWh -', 
          'min', round(mtx.min(),2),
          'mean', round(mtx.mean(),2),
          'max', round(mtx.max(),2))

# pick the mean values of arrays
for year in years_ls:
    for key in ENR_params[year]['out']:
        if type(ENR_params[year]['out'][key]) == np.ndarray:
            
            map_nonan = ~np.isnan(ENR_params[year]['out'][key])
            ENR_params[year]['out'][key] =\
                ENR_params[year]['out'][key][map_nonan].mean(dtype=float)
            
# export data for cost-brekdown analysis
with open(path_out_b+'ENR_params.json', 'w') as json_file:
    json.dump(ENR_params, json_file)    

#%%

############################################################################### 
# COST OF AMMONIA CALCULATION - eHB
###############################################################################   
 
for year in years_ls:    
    
    print('\n*** YEAR', year) 

    # convert capex electrolyser (EUR/kWel) into (EUR/t_Nh3) 
    T = eHB_params[year]['lifetime']
    
    if system == 'grid':
        cf = eHB_params[year]['capacity factor']
    elif system == 'agrivolt':
        cf = data_mtx['capacity_factor']
    else:
        raise OSError 
    
    eHB_params[year]['out']['capacity factor'] = cf
    
    conversion_coeff =\
        (T*cf*8760*eHB_params[year]['efficiency electrolyzer']*\
         m_ratio_NH3toH2/(1000*LHV_H2))

    # capex electrolyzer (EUR/t_NH3)
    eHB_params[year]['out']['capex EL'] =\
        eHB_params[year]['capex electrolyzer']/conversion_coeff         
        
    # capex Haber Bosch reactor (EUR/t_NH3)
    eHB_params[year]['out']['capex HB'] =\
        eHB_params[year]['capex Haber Bosch normal.']
        
    # cost ASU (EUR/t_NH3)
    eHB_params[year]['out']['ASU cost'] =\
        eHB_params[year]['out']['capex HB']*\
            eHB_params[year]['ASU capex fraction']
        
    # cost OandM (EUR/t_NH3)
    eHB_params[year]['out']['OandM cost'] =\
        eHB_params[year]['OandM capex fraction']*\
            (eHB_params[year]['out']['capex HB']+\
             eHB_params[year]['out']['capex EL'])                                            
    
    if system == 'grid':
        # storage cost (EUR/t_NH3)    
        eHB_params[year]['out']['storage cost'] = 0
    elif system == 'agrivolt':
        # storage cost (EUR/t_NH3)    
        eHB_params[year]['out']['storage cost'] =\
            eHB_params[year]['storage fraction']*\
            (eHB_params[year]['out']['capex HB'] +\
            eHB_params[year]['out']['capex EL']+\
            eHB_params[year]['out']['OandM cost'])
    else:
        raise OSError  
        
    # fixed costs (EUR/t_NH3)
    eHB_params[year]['out']['fixed cost'] =\
        eHB_params[year]['out']['capex HB'] +\
        eHB_params[year]['out']['capex EL']+\
        eHB_params[year]['out']['ASU cost'] +\
        eHB_params[year]['out']['OandM cost']+\
        eHB_params[year]['out']['storage cost']
        
    eHB_params[year]['out']['varc - electrolyzer'] =\
        LHV_H2/eHB_params[year]['efficiency electrolyzer']/m_ratio_NH3toH2*\
            LevCost['LCOE_PV'][year]

    eHB_params[year]['out']['varc - HB'] =\
        eHB_params[year]['energy required HB plant']*LevCost['LCOE_PV'][year]
        
    eHB_params[year]['out']['varc - ASU'] =\
        eHB_params[year]['ASU energy consumption']*LevCost['LCOE_PV'][year]
        
    # variable cost (EUR/t_NH3)
    eHB_params[year]['out']['variable cost'] =\
        eHB_params[year]['out']['varc - electrolyzer']+\
        +eHB_params[year]['out']['varc - HB']+\
        eHB_params[year]['out']['varc - ASU']                
        
    LevCost['LCOA_EHB'][year] = eHB_params[year]['out']['fixed cost'] +\
        eHB_params[year]['out']['variable cost']
    
    mtx = LevCost['LCOA_EHB'][year][LevCost['LCOA_EHB'][year]==\
                                    LevCost['LCOA_EHB'][year]]
    print('LCOA - eHB EUR/MWh -', 
          'min', round(mtx.min(),2),
          'mean', round(mtx.mean(),2),
          'max', round(mtx.max(),2))
    
# pick the mean values of arrays
for year in years_ls:
    for key in eHB_params[year]['out']:
        if type(eHB_params[year]['out'][key]) == np.ndarray:
            
            map_nonan = ~np.isnan(eHB_params[year]['out'][key])
            eHB_params[year]['out'][key] =\
                eHB_params[year]['out'][key][map_nonan].mean(dtype=float)
                
# export data for cost-brekdown analysis
with open(path_out_b+'EHB_params.json', 'w') as json_file:
    json.dump(eHB_params, json_file)         
  
#%% export country-specific statistics of cost distribution   

path_c = '../input_data/data_csv/'
filename_c = 'data_country.csv'
c_df = pd.read_csv(path_c+filename_c)

country_ls = np.sort(c_df.country.drop_duplicates().dropna().tolist())

for metric in metrics_ls:
    
    lco = {}
    
    for year in years_ls:
            
        LevCost[metric][year][LevCost[metric][year]<1e-3] = np.nan
        LevCost_raster[metric][year].values[:,:,:] =\
            LevCost[metric][year][:,:,:]
        
        if 'LCOE' in metric:
            
            um_str = 'EUR_MWh'
                    
            LevCost_raster[metric][year].rio.to_raster(path_out+\
                f'{metric}_{um_str}-{year}.tif',
                driver='GTIFF') 

        elif 'LCOE' not in metric:

            um_str = 'EUR_t'
                
            LevCost_raster[metric][year].rio.to_raster(path_out+\
                f'{metric}_{um_str}-{year}.tif',
                driver='GTIFF')     

        # convert to dataframe
        df = pd.DataFrame()
        
        path_tifref = '../input_data/data_tif/'
        filename_ref = 'current_syn_nitrogen-2020-reproj.tif'
        tif_Ref = rxr.open_rasterio(
            path_tifref+filename_ref, masked=True)
        
        rds = tif_Ref.squeeze().drop_vars(["spatial_ref", "band"])
        rds.name = 'nitrogen'
        data_df = rds.to_dataframe().reset_index()
        map_nonan = data_df['nitrogen'] == data_df['nitrogen']
        
        rds2 =\
            LevCost_raster[metric][year].squeeze().drop_vars(["spatial_ref", "band"])
        rds2.name = metric
        data_df2 = rds2.to_dataframe().reset_index()
        
        var_name = metric+f'_EUR_MWh-{year}'
        lco[var_name] =  data_df2[map_nonan].loc[:,[metric]]
        lco[var_name]['country'] = c_df.country.values    
    
        df_lco_c = pd.DataFrame(index=country_ls)      

        for c in country_ls:
            
            map_c = (lco[var_name].country.values == c)
            values = lco[var_name].loc[map_c, metric]
            
            df_lco_c.loc[c, 'mean'] = values.mean()
            df_lco_c.loc[c, 'median'] = values.median()
            df_lco_c.loc[c, 'min'] = values.min()
            df_lco_c.loc[c, 'max'] = values.max() 
            df_lco_c.loc[c, 'std'] = values.std()
            
        df_lco_c.to_csv(path_out_c+f'{metric}_{um_str}-{year}.csv')
