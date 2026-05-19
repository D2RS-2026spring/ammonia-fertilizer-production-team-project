#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:25:58 2023

    Script to compute the Sobol index from the DOE matrix of samples generated

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

from SALib.analyze import sobol
import pandas as pd
import numpy as np
import os
import rioxarray as rxr
import matplotlib.pyplot as plt

path_out = './output/sensitivity/'
try:
    os.makedirs(path_out)
except OSError:
    pass

output_df = pd.DataFrame()
bounds_df = pd.read_csv(path_out+'/DOE_bounds.csv', index_col=0)

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

input_param_ls = [
    'lifetime',
    'degradation_rate',
    'capex',
    'OandM_expenses-fixed',
    'panel_to_soil_surf',
    'conversion_efficiency'
    ]
    
PV_params = {}
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

LevCost, LevCost_raster = {}, {}
metrics_ls = ['LCOE_PV', 'LCOA_ENR', 'LCOA_EHB']
    
for metric in metrics_ls:    
    LevCost[metric] = {}

eHB_params = {}
for year in years_ls:  
    eHB_params[year] = {}
    eHB_params[year]['out'] = {}
    for param in input_param_ls:
        eHB_params[year][param] =\
            eHB.loc[eHB.year==year].loc[param,'value'].item() 

# capacity factor (-)
data_mtx['capacity_factor'] = data_mtx['PVOUT']/hours_d

system = 'agrivolt'

var_names_DOE = {
    'discount_rate':'discount_rate',
    'capex_PV':'capex_PV',    
    }

for year in years_ls:
    
    print('\n*** YEAR', year) 
    
    samples_df = pd.read_csv(path_out+f'/Saltelli_values-{year}.csv')
    samples_arr = samples_df.index.values
    
    for i in samples_arr:
        
        for var in samples_df.columns.values:
            
            index = '-'.join(var.split('-')[:-1])
            
            if 'GEN' in var.split('-'):
                map_vars = (GEN.index.values==index)
                map_years = (GEN.loc[:, 'year']==year)
                GEN.loc[map_vars&map_years, 'value'] = samples_df.loc[i, var]                
                
            if 'PV' in var.split('-'):                     
                PV_params[year][index] = samples_df.loc[i, var]  

            if 'ENR' in var.split('-'):                   
                ENR_params[year][index] = samples_df.loc[i, var]   

            if 'eHB' in var.split('-'):                
                eHB_params[year][index] = samples_df.loc[i, var]                      
            
            # var_ref = 'capex-PV'
            # if var == var_ref:
            #     print('-----', var_ref,
            #           PV_params[year][index],
            #           samples_df.loc[i,var_ref]
            #           )                
            # var_ref = 'faradaic efficiency-ENR'
            # if var == var_ref:
            #     print('-----', var_ref,
            #           ENR_params[year][index],
            #           samples_df.loc[i,var_ref]
            #           )     
            # var_ref = 'storage fraction-eHB'
            # if var == var_ref:
            #     print('-----', var_ref,
            #           eHB_params[year][index],
            #           samples_df.loc[i,var_ref]
            #           )    
                
        conv_USD_EUR = GEN[GEN['year']==2022].loc['usd_to_eur', 'value']
        LHV_H2 = GEN.loc['LHV H2', 'value']
        LHV_NH3 = GEN.loc['LHV NH3', 'value']
        m_ratio_NH3toH2 = GEN.loc['mass ratio', 'value']                
        
        print('\tsample', i+1, '/', samples_arr.size)

        #######################################################################
        # LCOE CALCULATION
        #######################################################################       
        
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
                          PV_params[year]['out']['capacity_MW']*\
                              (1-d)**t)/(1+r)**t\
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
        
        #######################################################################
        # COST OF AMMONIA CALCULATION - ENR
        #######################################################################
        
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
    
        #######################################################################
        # COST OF AMMONIA CALCULATION - eHB
        #######################################################################
        
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

        ####################################################################### 
        
        _values = LevCost['LCOE_PV'][year][LevCost['LCOE_PV'][year]==\
                                            LevCost['LCOE_PV'][year]]
        output_df.loc[i, f'LCOE_PV_{year}-mean'] = _values.mean()
        output_df.loc[i, f'LCOE_PV_{year}-median'] = np.median(_values)
        output_df.loc[i, f'LCOE_PV_{year}-std'] = _values.std()
        
        _values = LevCost['LCOA_ENR'][year][LevCost['LCOA_ENR'][year]==\
                                            LevCost['LCOA_ENR'][year]]
        output_df.loc[i, f'LCOA_ENR_{year}-mean'] = _values.mean()
        output_df.loc[i, f'LCOA_ENR_{year}-median'] = np.median(_values)
        output_df.loc[i, f'LCOA_ENR_{year}-std'] = _values.std()
        
        _values = LevCost['LCOA_EHB'][year][LevCost['LCOA_EHB'][year]==\
                                            LevCost['LCOA_EHB'][year]]
        output_df.loc[i, f'LCOA_EHB_{year}-mean'] = _values.mean()
        output_df.loc[i, f'LCOA_EHB_{year}-median'] = np.median(_values)
        output_df.loc[i, f'LCOA_EHB_{year}-std'] = _values.std()        
        
#%% Sobol analysis

problem = {
    'num_vars': samples_df.columns.size,
    'names': samples_df.columns.tolist(),
    'bounds': bounds_df.values
    }

for metric in ['LCOE_PV', 'LCOA_ENR', 'LCOA_EHB']:
    for year in years_ls:
        for stat in ['mean', 'median', 'std']:
            
            key = f'{metric}_{year}-{stat}'
            
            print(metric, year, stat)
            Y = output_df[key].values
            Si = sobol.analyze(problem, Y, print_to_console=True,
                                calc_second_order=False)
            total_Si, first_Si = Si.to_df()
            
            print(key, first_Si.sum())
            
            plt.figure()
            Si.plot()
            plt.title(key)
            
            df_out = pd.DataFrame(Si, index=samples_df.columns)            
            df_out.to_csv(path_out+f'sobol-{key}.csv', index=True)
            