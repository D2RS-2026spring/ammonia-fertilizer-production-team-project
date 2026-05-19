#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 14:24:16 2023

    Script to compute the design of experiment matrix based on the
    latin hypercube

@author: Davide Tonelli, PhD candidate UCLouvain
         davide.tonelli@uclouvain.be
         davidetonelli@outlook.com
"""

import pandas as pd
import numpy as np
import os
from pyDOE import lhs
from SALib.sample import sobol

## dictionary with all the data
path = './input/'
filename = 'parameters_cost.xlsx'

data_techs_excel = pd.read_excel(path+filename, engine='openpyxl', 
                                 sheet_name=None)
GEN = data_techs_excel['general'].set_index('parameter')
PV = data_techs_excel['PV'].set_index('parameter')
ENR = data_techs_excel['ENR'].set_index('parameter')
eHB = data_techs_excel['eHB'].set_index('parameter')

path_out = './output/sensitivity/'
try:
    os.makedirs(path_out)
except OSError:
    pass

def latin_hypercube(n, bounds):
    """
    Generate a Latin hypercube sample of size n over the specified bounds
    using the pyDOE library.
    
    Parameters:
    n (int): the number of samples to generate
    bounds (list of tuples): the bounds for each parameter as a list of tuples
        (lower, upper)
    
    Returns:
    samples (numpy array): an n x k numpy array containing the Latin hypercube sample
    """
    
    k = len(bounds)
    samples = lhs(k, samples=n, criterion='maximin')
    
    # Scale the samples to the specified bounds
    for i in range(k):
        lower, upper = bounds[i]
        samples[:,i] = lower + samples[:,i] * (upper - lower)
        
    return samples

variables_ls = [
    
    ## general
    'discount_rate-GEN',
    
    ## PV
    'capex-PV',
    # 'lifetime-PV',
    'degradation_rate-PV',
    'OandM_expenses-fixed-PV',
    # 'conversion_efficiency-PV',
    # 'panel_to_soil_surf-PV',
    
    ## ENR
    # 'enthalphy reaction-ENR',
    'faradaic efficiency-ENR',
    # 'theoretical voltage-ENR',
    # 'overpotential-ENR',
    'capex electrolyzer-ENR',
    # 'efficiency electrolyzer-ENR',
    # 'OandM capex fraction-ENR',
    # 'ASU capex fraction-ENR',
    # 'ASU energy consumption-ENR',
    # 'capacity factor-ENR',
    # 'lifetime-ENR',
    
    ## eHB
    'capex electrolyzer-eHB',
    'efficiency electrolyzer-eHB',
    # 'capex Haber Bosch normal.-eHB',
    # 'energy required HB plant-eHB',
    'storage fraction-eHB',
    # 'OandM capex fraction-eHB',
    # 'ASU capex fraction-eHB',
    # 'ASU energy consumption-eHB',
    # 'capacity factor-eHB',
    # 'lifetime-eHB'
        
    ]

N_variables = len(variables_ls)
N_samples = 2**4

for year in [2020, 2030, 2050]:
    
    print('\n# year', year)
    
    samples = np.empty([N_samples, N_variables])
    bounds = list()
    
    for variable in variables_ls:          
        
        # general            
        if 'GEN' in variable.split('-'):
            
            df = GEN[GEN.year==year]             
        
        # PV     
        if 'PV' in variable.split('-'):
            
            df = PV[PV.year==year]     
            
        # ENR
        if 'ENR' in variable.split('-'):
            
            df = ENR[ENR.year==year]

        # eHB		
        if 'eHB' in variable.split('-'):
            
            df = eHB[eHB.year==year]       
    
        index = '-'.join(variable.split('-')[:-1])  
        
        lb = min([df.loc[index,'pess'], df.loc[index,'opt']])
        ub = max([df.loc[index,'pess'], df.loc[index,'opt']])
        
        bounds.append((lb,ub))
    
    for iv in range(len(variables_ls)):
        print(list(zip(variables_ls, bounds))[iv][0],
              list(zip(variables_ls, bounds))[iv][1])
    
    # hypercube matrix: (samples, variables)    
    samples[:,:] = latin_hypercube(N_samples, bounds)
    
    problem = {
        'num_vars': N_variables,
        'names': variables_ls,
        'bounds': bounds,
        'sample_scaled': False
    }
    
    # Saltelli sampler
    samples_Saltelli = sobol.sample(problem, N_samples, 
                                    calc_second_order=False,
                                    )
    
    df_out = pd.DataFrame(samples, columns=variables_ls)
    df_out.to_csv(path_out+f'/LHC_values-{year}.csv', index=False)
    
    df_out = pd.DataFrame(samples_Saltelli, columns=variables_ls)
    df_out.to_csv(path_out+f'/Saltelli_values-{year}.csv', index=False)
    
    df_bounds = pd.DataFrame(bounds, index=variables_ls, columns=['min', 'max'])
    df_bounds.to_csv(path_out+'/DOE_bounds.csv', index=True)    