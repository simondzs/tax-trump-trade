#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 17:13:40 2024

@author: dora
"""

import funcs_for_dora as f
import pandas as pd
import numpy as np
from configurations import configurations

# Get country and sector lists
country_list = f.get_country_list()
sector_list = f.get_sector_list()

# # Create baseline
baseline = f.baseline(year=2018,
                      data_path='./data/',
                      exclude_direct_emissions=False)
#baseline.tariff.loc['USA',:,:] = 0.1
baseline.make_np_arrays(inplace=True)
baseline.compute_shares_and_gammas(inplace=True)

# Loop over configurations
for config in configurations:
    # Create tax matrix
    tax_matrix = pd.DataFrame(index=pd.MultiIndex.from_product([country_list, 
                                                                sector_list, 
                                                                country_list],
                        names=['row_country', 'row_sector', 'col_country']),
                        columns=['value'])
    tax_matrix['value'] = 0.0
    
    # Apply tax matrix scenarios
    for scenario in config['tax_matrix_scenario']:
        tax_matrix.loc[scenario[0], scenario[1], scenario[2]] = scenario[3]
        
    #this line takes the maximum between the existing tariff and the tax scenario
    #tax_matrix['value'] = np.maximum(tax_matrix.value,baseline.tariff.tariff)
    
    #tax_matrix['value'] =baseline.tariff.tariff
    
    # Create params
    par = f.params(data_path='./data/',
#                   eta_path="cp_estimate_allyears.csv", 
#                   sigma_path="cp_estimate_allyears.csv",
#                   eta_path="rescaled_to_4elasticities_agg2.csv", 
#                   sigma_path="rescaled_to_4elasticities_agg2.csv",
                   eta_path="fgo_estimate.csv", 
                   sigma_path="fgo_estimate.csv",                   
                   tax_matrix=tax_matrix)

    # Solve
    print(f'Solving {config["name"]}')
    results = f.solve_one_loop(params=par, baseline=baseline, vec_init=None, tol=1e-9, damping=10)
    
    # Write solution to CSV
    f.write_solution_csv(results=results,
#                         results_path='./results_dora/',
#                         results_path='./results_dora/rescaled4agg2/',
                         results_path='./results_dora/fgo/',
                         run_name=config['name'],
                         params=par)

    # Compute solution
    sol = f.sol(
                #results_path=f'results_dora/{config["name"]}_results.csv', 
                #tax_matrix_path=f'results_dora/{config["name"]}_tax_matrix.csv', 
#                results_path=f'results_dora/rescaled4agg2/{config["name"]}_results.csv', 
#                tax_matrix_path=f'results_dora/rescaled4agg2/{config["name"]}_tax_matrix.csv', 
                results_path=f'results_dora/fgo/{config["name"]}_results.csv', 
                tax_matrix_path=f'results_dora/fgo/{config["name"]}_tax_matrix.csv', 
                baseline=baseline, 
                data_path='data/',
                eta_path="fgo_estimate.csv", 
                sigma_path="fgo_estimate.csv")
#                eta_path="rescaled_to_4elasticities_agg2.csv", 
#                sigma_path="rescaled_to_4elasticities_agg2.csv")
#                eta_path="cp_estimate_allyears.csv", 
#                sigma_path="cp_estimate_allyears.csv")

    sol.compute_solution(baseline)
