#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 16:04:22 2024

@author: slepot
"""

import funcs_for_dora as f
import pandas as pd

tax_matrix = pd.DataFrame(index = pd.MultiIndex.from_product([f.get_country_list(),
                                                            f.get_sector_list(),
                                                            f.get_country_list()],
                                                            names = ['row_country',
                                                                    'row_sector',
                                                                    'col_country']),
                        columns = ['value'])
tax_matrix['value'] = 0.0



#test1
# tax_matrix.loc['USA',:,:] = 0.1
# tax_matrix.loc['USA',:,'USA'] = 0
# tax_matrix.loc[:,:,'NOR'] = 0.2
# tax_matrix.loc[:,'01T02',:] = 0.3
# tax_matrix.loc['BRA','01T02','CHN'] = 1.1


# =============================================================================
# #10 percent wordwide US to everyone
# tax_matrix.loc['USA',:,:] = 0.1
# tax_matrix.loc['USA',:,'USA'] = 0
# 
# =============================================================================

#10 percent wordwide, 60 to china
tax_matrix.loc['USA',:,:] = 0.1
tax_matrix.loc['USA',:,'USA'] = 0
tax_matrix.loc['USA',:,'CHN'] = 0.6


#%%

par = f.params(data_path='./data/',
             eta_path="cp_estimate_allyears.csv", 
             sigma_path="cp_estimate_allyears.csv",
             tax_matrix=tax_matrix
             )

baseline = f.baseline(year=2018,
                      data_path='./data/',
                      exclude_direct_emissions=False)

baseline.make_np_arrays(inplace = True)

baseline.compute_shares_and_gammas(inplace = True)

#%%

import funcs_for_dora as f

results = f.solve_one_loop(
                    params=par, 
                    baseline=baseline, 
                    vec_init = None, 
                    tol=1e-9, 
                    damping=5)

#%%

import funcs_for_dora as f

# =============================================================================
# f.write_solution_csv(results=results,
#                      results_path='./results_dora/',
#                      run_name ='the_first_test',
#                      params = par)
# 
# =============================================================================

# =============================================================================
# f.write_solution_csv(results=results,
#                      results_path='./results_dora/',
#                      run_name ='US10',
#                      params = par)
# 
# =============================================================================

f.write_solution_csv(results=results,
                     results_path='./results_dora/',
                     run_name ='US1060',
                     params = par)



#%%

import funcs_for_dora as f

# =============================================================================
# sol = f.sol(results_path='results_dora/the_first_test_results.csv', 
#             tax_matrix_path='results_dora/the_first_test_tax_matrix.csv', 
#             baseline=baseline, 
#             data_path='data/',
#             eta_path="cp_estimate_allyears.csv", 
#             sigma_path="cp_estimate_allyears.csv")
# 
# 
# =============================================================================

# =============================================================================
# sol = f.sol(results_path='results_dora/US10_results.csv', 
#             tax_matrix_path='results_dora/US10_tax_matrix.csv', 
#             baseline=baseline, 
#             data_path='data/',
#             eta_path="cp_estimate_allyears.csv", 
#             sigma_path="cp_estimate_allyears.csv")
# 
# =============================================================================


sol = f.sol(results_path='results_dora/US1060_results.csv', 
            tax_matrix_path='results_dora/US1060_tax_matrix.csv', 
            baseline=baseline, 
            data_path='data/',
            eta_path="cp_estimate_allyears.csv", 
            sigma_path="cp_estimate_allyears.csv")


sol.compute_solution(baseline)


#%% Get code for creating input output matrix


#it should be all part of sol

sol.iot
sol.cons


#%% Graphs

import funcs_for_dora as f
import matplotlib.pyplot as plt

fig,ax = plt.subplots()

sectors = f.get_sector_list()
y = sol.labor_hat.loc['NOR',:]

ax.bar(sectors,y.value*100-100)

plt.show()


