#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 18:01:10 2024

@author: dora
"""

import funcs_for_dora as f
import matplotlib.pyplot as plt
from configurations import configurations

#Right now, only one plot is turned on in configurations

# Create baseline
baseline = f.baseline(year=2018,
                      data_path='./data/',
                      exclude_direct_emissions=False)
baseline.make_np_arrays(inplace=True)
baseline.compute_shares_and_gammas(inplace=True)

# Dictionary to store solutions
solutions = {}

# Loop over configurations
for config in configurations:
# Compute solution
    sol = f.sol(
#            results_path=f'results_dora/{config["name"]}_results.csv', 
#            tax_matrix_path=f'results_dora/{config["name"]}_tax_matrix.csv', 
            results_path=f'results_dora/fgo/{config["name"]}_results.csv', 
            tax_matrix_path=f'results_dora/fgo/{config["name"]}_tax_matrix.csv', 
            baseline=baseline, 
            data_path='data/',
#            eta_path="cp_estimate_allyears.csv", 
#            sigma_path="cp_estimate_allyears.csv"
            eta_path="fgo_estimate.csv", 
            sigma_path="fgo_estimate.csv"
            )
    sol.compute_solution(baseline)
    solutions[config["name"]] = sol


#%% Setup
import os
# Define paths
#elasticities_path = 'cp_estimate_allyears' 
# elasticities_path = 'uniform_elasticities_4'
# elasticities_path = 'rescaled_to_4elasticities_agg2'
elasticities_path = 'fgo_estimate'
# options are 'cp_estimate_allyears.csv' (Caliendo) or 'uniform_elasticities_4.csv' or 'rescaled_to_4elasticities_agg2.csv' (Fontagne)

save_path = f'output/{elasticities_path}/'
save_format = 'pdf'
def make_directory(path):
    try:
        os.mkdir(path)
    except:
        pass
make_directory(save_path)


#%% SCENARIO GRAPHS
#%%Output for each scenario

#sum baseline output across sectors
baseline_output = baseline.output.groupby('country')['value'].sum()
baseline_output = baseline_output ['NOR']

# Calculate the sum of 'variable1' for each scenario
sumsoutput = {}
# Add baseline output to sumsoutput with a unique key
sumsoutput['Baseline'] = baseline_output

for config_name, sol in solutions.items():
#sum output across sectors
    summed_output = sol.output.groupby('country')['value'].sum()
    summed_output = summed_output['NOR']
    sumsoutput[config_name] = summed_output
    
# Calculate percent change relative to baseline
percent_changes = {}
for key, value in sumsoutput.items():
    if key == 'Baseline':
        percent_changes[key] = 0.0  # Baseline itself has 0% change
    else:
        percent_change = ((value - baseline_output) / baseline_output) * 100
        percent_changes[key] = percent_change
    
# Create a bar graph
plt.bar(sumsoutput.keys(), sumsoutput.values())
plt.ylabel('Output')

# Adding percent change as text on top of bars
for key, value in sumsoutput.items():
    if key != 'Baseline':
        plt.text(key, value + 0.05 * max(sumsoutput.values()), f'{percent_changes[key]:.1f}%', ha='center')

plt.xticks(rotation=45)  # Rotate x labels if they are too long

# Adjust y-axis limits to make space for text annotations
max_output = max(sumsoutput.values())
plt.ylim(0, max_output + 0.1 * max_output)  # Adjust as needed for spacing

plt.tight_layout()  # Adjust layout to make room for the x labels
plt.show()


#adjust axes - what values is this in?


#%% Output on and offshore for each scenario
import pandas as pd
import matplotlib.pyplot as plt
from configurations import sector_classification


# Example baseline data (replace with your actual data and access method)
baseline_output = baseline.output.loc['NOR']

#add new column sector name
baseline_output['sectorname']=f.get_sector_names_list()

#add new column on and offshore
baseline_output['OnOffshore'] = baseline_output['sectorname'].map(lambda x: sector_classification[x]['OnOffshore'] if x in sector_classification else 'Unknown')

# Aggregate data by 'OnOffshore' and sum the values
agg_output = baseline_output.groupby('OnOffshore')['value'].sum()

#for percent calculation
tot_output = baseline.output.groupby('country')['value'].sum()
tot_output = tot_output['NOR']

# Calculate the sum of 'variable1' for each scenario
sumsoutput = {}
totaloutput={}
# Add baseline output to sumsoutput with a unique key
sumsoutput['Baseline'] = agg_output
totaloutput['Baseline'] = tot_output

for config_name, sol in solutions.items():
    sol_output = sol.output.loc['NOR']
    #add new column sector name
    sol_output['sectorname']=f.get_sector_names_list()
    #add new column on and offshore
    sol_output['OnOffshore'] = sol_output['sectorname'].map(lambda x: sector_classification[x]['OnOffshore'] if x in sector_classification else 'Unknown')
    # Aggregate data by 'OnOffshore' and sum the values
    summed_output = sol_output.groupby('OnOffshore')['value'].sum()
    sumsoutput[config_name] = summed_output
#for percent calculation
    tot_output = sol.output.groupby('country')['value'].sum()
    tot_output = tot_output['NOR']
    totaloutput[config_name] = tot_output


# Calculate percent change relative to baseline
baseline_total = totaloutput['Baseline']
percent_changes_output = {}
for key, value in totaloutput.items():
    if key == 'Baseline':
        percent_changes_output[key] = 0.0  # Baseline itself has 0% change
    else:
        percent_change = ((value - baseline_total ) / baseline_total ) * 100
        percent_changes_output[key] = percent_change

# Convert sumsoutput dictionary to DataFrame and transpose it
sumsoutput_df = pd.DataFrame(sumsoutput).T


# Plot stacked bar chart
#ax[0,0].plt.figure(figsize=(10, 6))
sumsoutput_df.plot(kind='bar', stacked=True, color=['blue', 'orange'], ax=plt.gca())  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, (key, value) in enumerate(totaloutput.items()):
    if key != 'Baseline':
        plt.text(i, value + 0.05 * max(totaloutput.values()), f'{percent_changes_output[key]:.1f}%', ha='center')

# Adjust y-axis limits to make space for text annotations
max_output = max(totaloutput.values())
#plt.lim(0, max_output + 0.1 * max_output)  # Adjust as needed for spacing

plt.ylabel('Total Output')
plt.title('Stacked Bar Chart of Output by Scenario and Onshore vs Offshore')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()

#adjust axes




#%% Exports onshore offshore for each scenario 

import pandas as pd
import matplotlib.pyplot as plt
from configurations import sector_classification


#exports and imports (from to)
baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade

#only exports, aggregate
baseline_exports=baseline_trade.groupby(['row_country', 'row_sector']).sum()
baseline_exports=baseline_exports.loc['NOR']

#onshore offshore sectors
#add new column sector name
baseline_exports['sectorname']=f.get_sector_names_list()
#add new column on and offshore
baseline_exports['OnOffshore'] = baseline_exports['sectorname'].map(lambda x: sector_classification[x]['OnOffshore'] if x in sector_classification else 'Unknown')
# Aggregate data by 'OnOffshore' and sum the values
baseline_exports = baseline_exports.groupby('OnOffshore')['value'].sum()
#for percent calculation
total_baseline_trade = baseline_exports.sum()

sumtrade={}
tottrade={}

# Add baseline output to sumsoutput with a unique key
sumtrade['Baseline'] = baseline_exports
tottrade['Baseline'] = total_baseline_trade


for config_name, sol in solutions.items():
    #exports and imports (from to)
    trade=sol.iot.groupby(['row_country','row_sector','col_country']).sum()+sol.cons
    trade=trade.query('row_country!=col_country') #dropped those rows for domestic trade

    #only exports, aggregate
    exports=trade.groupby(['row_country', 'row_sector']).sum()
    exports=exports.loc['NOR']

    #onshore offshore sectors
    #add new column sector name
    exports['sectorname']=f.get_sector_names_list()
    #add new column on and offshore
    exports['OnOffshore'] = exports['sectorname'].map(lambda x: sector_classification[x]['OnOffshore'] if x in sector_classification else 'Unknown')
    # Aggregate data by 'OnOffshore' and sum the values
    exports = exports.groupby('OnOffshore')['value'].sum()
    sumtrade[config_name] = exports
    #for percent calculation
    total_trade = exports.sum()
    tottrade[config_name] = total_trade


# Convert sumsoutput dictionary to DataFrame and transpose it
sumtrade_df = pd.DataFrame(sumtrade).T


# Calculate percent change relative to baseline
baseline_total = tottrade['Baseline']
percent_changes_trade = {}
for key, value in tottrade.items():
    if key == 'Baseline':
        percent_changes_trade[key] = 0.0  # Baseline itself has 0% change
    else:
        percent_change = ((value - baseline_total ) / baseline_total ) * 100
        percent_changes_trade[key] = percent_change


# Plot stacked bar chart
plt.figure(figsize=(10, 6))
sumtrade_df .plot(kind='bar', stacked=True, color=['blue', 'orange'], ax=plt.gca())  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, (key, value) in enumerate(tottrade.items()):
    if key != 'Baseline':
        #plt.text(i, 100*(value-total_baseline_trade)/value, f'{percent_changes[key]:.1f}%', ha='center')
        plt.text(i, value + 0.05 * max(tottrade.values()), f'{percent_changes_trade[key]:.1f}%', ha='center')

# Adjust y-axis limits to make space for text annotations
max_output = max(tottrade.values())
plt.ylim(0, max_output + 0.1 * max_output)  # Adjust as needed for spacing

plt.ylabel('Total Exports')
plt.title('Stacked Bar Chart of Exports by Scenario and Onshore vs Offshore')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()

#adjust axes

#%% Imports onshore offshore for each scenario 

import pandas as pd
import matplotlib.pyplot as plt
from configurations import sector_classification


#exports and imports (from to)
baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade

#only imports, aggregate
baseline_imports=baseline_trade.groupby(['col_country', 'row_sector']).sum()
baseline_imports=baseline_imports.loc['NOR']

#onshore offshore sectors
#add new column sector name
baseline_imports['sectorname']=f.get_sector_names_list()
#add new column on and offshore
baseline_imports['OnOffshore'] = baseline_imports['sectorname'].map(lambda x: sector_classification[x]['OnOffshore'] if x in sector_classification else 'Unknown')
# Aggregate data by 'OnOffshore' and sum the values
baseline_imports= baseline_imports.groupby('OnOffshore')['value'].sum()
#for percent calculation
total_baseline_imports = baseline_imports.sum()

sumimports={}
totimports={}

# Add baseline output to sumsoutput with a unique key
sumimports['Baseline'] = baseline_imports
totimports['Baseline'] = total_baseline_imports


for config_name, sol in solutions.items():
    #exports and imports (from to)
    trade=sol.iot.groupby(['row_country','row_sector','col_country']).sum()+sol.cons
    trade=trade.query('row_country!=col_country') #dropped those rows for domestic trade

    #only imports, aggregate
    imports=trade.groupby(['row_country', 'row_sector']).sum()
    imports=imports.loc['NOR']

    #onshore offshore sectors
    #add new column sector name
    imports['sectorname']=f.get_sector_names_list()
    #add new column on and offshore
    imports['OnOffshore'] = imports['sectorname'].map(lambda x: sector_classification[x]['OnOffshore'] if x in sector_classification else 'Unknown')
    # Aggregate data by 'OnOffshore' and sum the values
    imports = imports.groupby('OnOffshore')['value'].sum()
    sumimports[config_name] = imports
    #for percent calculation
    total_trade = imports.sum()
    totimports[config_name] = total_trade


# Convert sumsoutput dictionary to DataFrame and transpose it
sumimports_df = pd.DataFrame(sumimports).T


# Calculate percent change relative to baseline
baseline_total = totimports['Baseline']
percent_changes_imports = {}
for key, value in totimports.items():
    if key == 'Baseline':
        percent_changes_imports[key] = 0.0  # Baseline itself has 0% change
    else:
        percent_change = ((value - baseline_total ) / baseline_total ) * 100
        percent_changes_imports[key] = percent_change


# Plot stacked bar chart
plt.figure(figsize=(10, 6))
sumimports_df .plot(kind='bar', stacked=True, color=['blue', 'orange'], ax=plt.gca())  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, (key, value) in enumerate(totimports.items()):
    if key != 'Baseline':
        plt.text(i, value + 0.05 * max(totimports.values()), f'{percent_changes_imports[key]:.1f}%', ha='center')
#        plt.text(i, 100*(value-total_baseline_trade)/value, f'{percent_changes[key]:.1f}%', ha='center')

# Adjust y-axis limits to make space for text annotations
max_output = max(totimports.values())
plt.ylim(0, max_output + 0.1 * max_output)  # Adjust as needed for spacing

plt.ylabel('Total Imports')
plt.title('Stacked Bar Chart of Imports by Scenario and Onshore vs Offshore')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()

#adjust axes



#%% Labor reallocation by off and onshore for each scenario

#Problem: There is no labor for baseline
import pandas as pd
import matplotlib.pyplot as plt
from configurations import sector_classification

sumlabor={}

for config_name, sol in solutions.items():

    #labor changes for Norway
    laborchange=abs(sol.labor_hat.loc['NOR']-1)
    #these values are now all positive

    #onshore offshore sectors
    #add new column sector name
    laborchange['sectorname']=f.get_sector_names_list()
    #add new column on and offshore
    laborchange['OnOffshore'] = laborchange['sectorname'].map(lambda x: sector_classification[x]['OnOffshore'] if x in sector_classification else 'Unknown')
    # Aggregate data by 'OnOffshore' and sum the values
    laborchange= laborchange.groupby('OnOffshore')['value'].sum()
    sumlabor[config_name] = 100*laborchange
    

# Convert sumsoutput dictionary to DataFrame and transpose it
sumlabor_df = pd.DataFrame(sumlabor).T

# Plot stacked bar chart
sumlabor_df.plot(kind='bar', stacked=True, color=['blue', 'orange'])  # Adjust colors as needed

plt.ylabel('Labor reallocation in percent')
plt.title('Stacked Bar Chart of Labor reallocation by Scenario and Onshore vs Offshore')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()


##

# Example baseline data (replace with your actual data and access method)
#baseline_labor  = baseline.labor[baseline.labor['country'] == 'NOR']['2018']

#define index
#baseline.labor.set_index('country')


#Labor_hat(country) = ( Sum(sector) Labor_hat(country,sector) * Labor_baseline(country*sector) ) / Labor_baseline(country)


#%%Plot all together

#start subplot
fig, ax = plt.subplots(2,2,figsize=(16,12))


# Plot stacked bar chart OUTPUT
#ax[0,0].plt.figure(figsize=(10, 6))
sumsoutput_df.plot(kind='bar', stacked=True, color=['blue', 'lightblue'], ax=ax[0, 0])  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, (key, value) in enumerate(totaloutput.items()):
    if key != 'Baseline':
        ax[0, 0].text(i, value + 0.05 * max(totaloutput.values()), f'{percent_changes_output[key]:.1f}%', ha='center')

# Adjust y-axis limits to make space for text annotations
max_output = max(totaloutput.values())

ax[0,0].set_ylim(0, max_output + 0.1 * max_output)  # Adjust as needed for spacing

ax[0,0].set_ylabel('Total Output in bn USD (2018)')

# Adjust y-axis tick labels to show values in billions
ax[0, 0].set_yticklabels([f'{int(tick / 1000)}' for tick in ax[0, 0].get_yticks()])

# Rotate x-axis labels
ax[0, 0].set_xticklabels(ax[0, 0].get_xticklabels(), rotation=45, ha='right')

# Set title
ax[0, 0].set_title('Output')

# Plot stacked bar chart LABOR
#add 0 baseline to labor
# Create a new DataFrame for the new row
new_row = pd.DataFrame({'onshore': [0], 'offshore': [0]}, index=['Baseline'])
# Concatenate the original DataFrame with the new row DataFrame
sumlabor_df2 = pd.concat([new_row, sumlabor_df])

sumlabor_df2.plot(kind='bar', stacked=True, color=['blue', 'lightblue'], ax=ax[0,1])  # Adjust colors as needed

ax[0,1].set_ylabel('Labor reallocation in percent')


# Rotate x-axis labels
ax[0, 1].set_xticklabels(ax[0, 1].get_xticklabels(), rotation=45, ha='right')


# Set title
ax[0, 1].set_title('Labor')

# Plot stacked bar chart EXPORTS
sumtrade_df.plot(kind='bar', stacked=True, color=['blue', 'lightblue'], ax=ax[1,0])  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, (key, value) in enumerate(tottrade.items()):
    if key != 'Baseline':
        ax[1,0].text(i, value + 0.05 * max(tottrade.values()), f'{percent_changes_trade[key]:.1f}%', ha='center')

# Adjust y-axis limits to make space for text annotations
max_trade = max(tottrade.values())
ax[1,0].set_ylim(0, max_trade + 0.1 * max_trade )  # Adjust as needed for spacing

ax[1,0].set_ylabel('Total Exports in bn USD (2018)')

# Adjust y-axis tick labels to show values in billions
ax[1, 0].set_yticklabels([f'{int(tick / 1000)}' for tick in ax[1, 0].get_yticks()])

# Rotate x-axis labels
ax[1, 0].set_xticklabels(ax[1, 0].get_xticklabels(), rotation=45, ha='right')

# Set title
ax[1, 0].set_title('Exports')

# Plot stacked bar chart IMPORTS
sumimports_df.plot(kind='bar', stacked=True, color=['blue', 'lightblue'], ax=ax[1,1])  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, (key, value) in enumerate(totimports.items()):
    if key != 'Baseline':
        ax[1,1].text(i, value + 0.05 * max(totimports.values()), f'{percent_changes_imports[key]:.1f}%', ha='center')

# Adjust y-axis limits to make space for text annotations
max_imports= max(totimports.values())
ax[1,1].set_ylim(0, max_imports + 0.1 * max_imports)  # Adjust as needed for spacing

ax[1,1].set_ylabel('Total Imports in bn USD (2018)')
ax[1,1].legend(loc='lower right')

# Adjust y-axis tick labels to show values in billions
ax[1, 1].set_yticklabels([f'{int(tick / 1000)}' for tick in ax[1, 1].get_yticks()])


# Rotate x-axis labels
ax[1, 1].set_xticklabels(ax[1, 1].get_xticklabels(), rotation=45, ha='right')

# Set title
ax[1, 1].set_title('Imports')

#hide other legends
ax[0, 0].legend().set_visible(False)  # Hide legend
ax[0, 1].legend().set_visible(False)  # Hide legend
ax[1, 0].legend().set_visible(False)  # Hide legend




plt.tight_layout(pad=3),

plt.savefig(save_path+'scenarios_output_labor_exports_imports.pdf',format=save_format)

plt.show()


#%% Utility

import pandas as pd
import matplotlib.pyplot as plt
#from configurations import sector_classification

utility={}
for config_name, sol in solutions.items():

    #utility changes for Norway
    utility[config_name] = 100*(abs(sol.utility.loc['NOR']-1))
    

# Convert sumsoutput dictionary to DataFrame and transpose it
utility_df = pd.DataFrame(utility).T

# Plot stacked bar chart
utility_df.plot(kind='bar', stacked=True)  # Adjust colors as needed

plt.ylabel('Utility change in percent')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.legend().remove()
plt.show()




#%% SECTORAL GRAPHS

#%% Output sector graph

from configurations import sector_classification, sector_colors

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

# Get baseline output
baseline_output=baseline.output.loc['NOR',:,:]

for config_name, sol in solutions.items():
    output = sol.output.loc['NOR', :]
    
    #Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    #percent calculation
    output_percent=100*(output-baseline_output)/output

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, output.value, color=colors)

    plt.xticks(rotation=45, ha='right')
    
    # Add percent_output on top of the bars
    for bar, percent in zip(bars, output_percent.value):
        height = bar.get_height()
        ax.annotate(
            f'{percent:.1f}%',  # Format the percentage with 2 decimal places
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            rotation=45,
            fontsize=12
        )


    # Set y-axis label
    ax.set_ylabel('Output (mn USD 2018)', fontsize=25)

    # Adjust axis limits to fit text, increasing the upper limit by 10%
    y_max = max(output.value)
    ax.set_ylim([min(output.value) - 3, y_max * 1.1])
    ax.set_xlim([-1, len(sectors)])

    #plt.title(f'{config_name}', fontsize=25)
    plt.savefig(f'{save_path}sectors_output_{config_name}.{save_format}', format=save_format)
    plt.show()


#%% Real output sector graph

#Todo: put the country labels on top of bars
#Todo: make font size larger for labels

from configurations import sector_classification, sector_colors

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

# Get baseline output
#baseline_output=baseline.output.loc['NOR',:,:]
baseline_output=baseline.output

for config_name, sol in solutions.items():
    #output = sol.output.loc['NOR', :]
    output = sol.output
    
    #Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    #create output hat
    output_hat_all=output/baseline_output
    output_hat_all=100*(output_hat_all-1)

    output_hat=output_hat_all.loc['NOR',:]
    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, output_hat.value, color=colors)

    plt.xticks(rotation=45, ha='right')
    
# =============================================================================
#     # Add percent_output on top of the bars
#     for bar, percent in zip(bars, output_percent.value):
#         height = bar.get_height()
#         ax.annotate(
#             f'{percent:.1f}%',  # Format the percentage with 2 decimal places
#             xy=(bar.get_x() + bar.get_width() / 2, height),
#             xytext=(0, 3),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',
#             rotation=45,
#             fontsize=12
#         )
# =============================================================================


    # Set y-axis label
    ax.set_ylabel('Change in Real Output (in %)', fontsize=25)

# =============================================================================
#     # Adjust axis limits to fit text, increasing the upper limit by 10%
#     y_max = max(output.value)
#     ax.set_ylim([min(output.value) - 3, y_max * 1.1])
#     ax.set_xlim([-1, len(sectors)])
# =============================================================================

    #plt.title(f'{config_name}', fontsize=25)
    #plt.savefig(f'{save_path}sectors_output_{config_name}.{save_format}', format=save_format)
    plt.show()



#%% Labor sector graph

from configurations import sector_classification, sector_colors

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

for config_name, sol in solutions.items():
    y = sol.labor_hat.loc['NOR', :]
    
    #Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, y.value * 100 - 100, color=colors)

    # Remove default x-tick labels
    ax.set_xticklabels([''])

    # Add labels on top of bars
    ax.bar_label(ax.containers[0],
                 labels=sectors,
                 rotation=90,
                 label_type='edge',
                 padding=5,
                 zorder=10,
                 fontsize=15)

    # Set y-axis label
    ax.set_ylabel('Labor reallocation (% of workforce)', fontsize=25)

    # Adjust axis limits to fit text
    ax.set_ylim([min(y.value * 100 - 100) - 3, max(y.value * 100 - 100) + 3])
    ax.set_xlim([-1, len(sectors)])

    #plt.title(f'{config_name}', fontsize=25)
    plt.savefig(f'{save_path}sectors_labor_{config_name}.{save_format}', format=save_format)
    plt.show()


#%% Export sector graph

from configurations import sector_classification, sector_colors

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

# Get baseline exports
baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
baseline_trade=baseline_trade.groupby(['row_country', 'row_sector']).sum()
baseline_exports=baseline_trade.loc['NOR',:,:]


for config_name, sol in solutions.items():
    trade=sol.iot.groupby(['row_country','row_sector','col_country']).sum()+sol.cons
    trade=trade.query('row_country!=col_country') #dropped those rows for domestic trade
    trade=trade.groupby(['row_country', 'row_sector']).sum()
    exports=trade.loc['NOR',:,:]

    
    #Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    #percent calculation
    exports_percent=100*(exports-baseline_exports)/exports

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, exports.value, color=colors)

    plt.xticks(rotation=45, ha='right')
    
    # Add percent_output on top of the bars
    for bar, percent in zip(bars, exports_percent.value):
        height = bar.get_height()
        ax.annotate(
            f'{percent:.1f}%',  # Format the percentage with 2 decimal places
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            rotation=45,
            fontsize=12
        )


    # Set y-axis label
    ax.set_ylabel('Exports (mn USD 2018)', fontsize=25)

    # Adjust axis limits to fit text, increasing the upper limit by 10%
    y_max = max(exports.value)
    ax.set_ylim([min(exports.value) - 3, y_max * 1.1])
    ax.set_xlim([-1, len(sectors)])

    #plt.title(f'{config_name}', fontsize=25)
    plt.savefig(f'{save_path}sectors_exports_{config_name}.{save_format}', format=save_format)
    plt.show()


#%% Real Export sector graph + DOES NOT WORK

from configurations import sector_classification, sector_colors

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

# Get baseline exports
baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
baseline_trade=baseline_trade.groupby(['row_country', 'row_sector']).sum()
baseline_exports=baseline_trade.loc['NOR',:,:]


for config_name, sol in solutions.items():
    trade=sol.iot.groupby(['row_country','row_sector','col_country']).sum()+sol.cons
    trade=trade.query('row_country!=col_country') #dropped those rows for domestic trade
    trade=trade.groupby(['row_country', 'row_sector']).sum()
    exports=trade.loc['NOR',:,:]

    
    #Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    #export change
    exportchange=exports/baseline_exports

    #price change
    pricechange=sol.price.loc['NOR',:,:]

    #real exports
    realexports=exportchange.value/pricechange.hat

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, realexports, color=colors)

    plt.xticks(rotation=45, ha='right')
    
    # Add percent_output on top of the bars
# =============================================================================
#     for bar, percent in zip(bars, exports_percent.value):
#         height = bar.get_height()
#         ax.annotate(
#             f'{percent:.1f}%',  # Format the percentage with 2 decimal places
#             xy=(bar.get_x() + bar.get_width() / 2, height),
#             xytext=(0, 3),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',
#             rotation=45,
#             fontsize=12
#         )
# 
# =============================================================================

    # Set y-axis label
    ax.set_ylabel('Change in real exports (in %)', fontsize=25)

    # Adjust axis limits to fit text, increasing the upper limit by 10%
    #y_max = max(realexports.value)
    #ax.set_ylim([min(realexports.value) - 3, y_max * 1.1])
    #ax.set_xlim([-1, len(sectors)])

    #plt.title(f'{config_name}', fontsize=25)
    #plt.savefig(f'{save_path}sectors_exports_{config_name}.{save_format}', format=save_format)
    plt.show()



#%% Import sector graph

from configurations import sector_classification, sector_colors

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

# Get baseline exports
baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
baseline_trade=baseline_trade.groupby(['col_country', 'row_sector']).sum()
baseline_imports=baseline_trade.loc['NOR',:,:]


for config_name, sol in solutions.items():
    trade=sol.iot.groupby(['row_country','row_sector','col_country']).sum()+sol.cons
    trade=trade.query('row_country!=col_country') #dropped those rows for domestic trade
    trade=trade.groupby(['col_country', 'row_sector']).sum()
    imports=trade.loc['NOR',:,:]

    
    #Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    #percent calculation
    imports_percent=100*(imports-baseline_imports)/imports

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, imports.value, color=colors)

    plt.xticks(rotation=45, ha='right')
    
    # Add percent_output on top of the bars
    for bar, percent in zip(bars, imports_percent.value):
        height = bar.get_height()
        ax.annotate(
            f'{percent:.1f}%',  # Format the percentage with 2 decimal places
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            rotation=45,
            fontsize=12
        )


    # Set y-axis label
    ax.set_ylabel('Imports (mn USD 2018)', fontsize=25)

    # Adjust axis limits to fit text, increasing the upper limit by 10%
    y_max = max(imports.value)
    ax.set_ylim([min(imports.value) - 3, y_max * 1.1])
    ax.set_xlim([-1, len(sectors)])

    #plt.title(f'{config_name}', fontsize=25)
    plt.savefig(f'{save_path}sectors_imports_{config_name}.{save_format}', format=save_format)
    plt.show()


#%% Sectoral Exports to US

from configurations import sector_classification, sector_colors

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

# Get baseline exports
baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
baseline_exports=baseline_trade.loc['NOR',:,'USA']


for config_name, sol in solutions.items():
    trade=sol.iot.groupby(['row_country','row_sector','col_country']).sum()+sol.cons
    trade=trade.query('row_country!=col_country') #dropped those rows for domestic trade
    exports=trade.loc['NOR',:,'USA']

    
    #Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    #percent calculation
    exports_percent=100*(exports-baseline_exports)/exports

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, exports.value, color=colors)

    plt.xticks(rotation=45, ha='right')
    
    # Add percent_output on top of the bars
    for bar, percent in zip(bars, exports_percent.value):
        height = bar.get_height()
        ax.annotate(
            f'{percent:.1f}%',  # Format the percentage with 2 decimal places
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            rotation=45,
            fontsize=12
        )


    # Set y-axis label
    ax.set_ylabel('Exports to US (mn USD 2018)', fontsize=25)

    # Adjust axis limits to fit text, increasing the upper limit by 10%
    y_max = max(exports.value)
    ax.set_ylim([min(exports.value) - 3, y_max * 1.1])
    ax.set_xlim([-1, len(sectors)])

    #plt.title(f'{config_name}', fontsize=25)
    plt.savefig(f'{save_path}sectors_exportsTOUS_{config_name}.{save_format}', format=save_format)
    plt.show()



#%% Prices sector graph

from configurations import sector_classification, sector_colors

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

for config_name, sol in solutions.items():
    p=sol.price.loc['NOR', :,:]

    #Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, p.hat * 100 - 100, color=colors)

    # Remove default x-tick labels
    ax.set_xticklabels([''])

    # Add labels on top of bars
    ax.bar_label(ax.containers[0],
                 labels=sectors,
                 rotation=90,
                 label_type='edge',
                 padding=5,
                 zorder=10,
                 fontsize=15)

    # Set y-axis label
    ax.set_ylabel('Price change in %', fontsize=25)

    # Adjust axis limits to fit text
    ax.set_ylim([min(p.hat* 100 - 100) - 3, max(p.hat* 100 - 100) + 3])
    ax.set_xlim([-1, len(sectors)])

    #plt.title(f'{config_name}', fontsize=25)
    plt.savefig(f'{save_path}sectors_prices_{config_name}.{save_format}', format=save_format)
    plt.show()


#%% COUNTRY GRAPHS
#THIS TAKES A FEW MINUTES TO RUN
#Here, we need a graph for each sector by country.

from configurations import sector_classification, sector_colors
import matplotlib.patches as mpatches

save_path = f'output/{elasticities_path}/country_sector_graphs/'


# Get sector list
sectors = f.get_sector_list()
# Create reverse lookup dictionary for sector names
reverse_lookup = {v['SectorCode']: k for k, v in sector_classification.items()}


baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
# Define the list of EU countries
eu_countries = {'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 
                'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 
                'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'}


#sec='01T02'

for sec in sectors:

    # Get baseline exports
    baseline_exports=baseline_trade.loc['NOR',sec,:]

    for config_name, sol in solutions.items():
        trade = sol.iot.groupby(['row_country', 'row_sector', 'col_country']).sum() + sol.cons
        trade = trade.query('row_country != col_country')  # dropped those rows for domestic trade
        exports = trade.loc['NOR', sec, :]

        # Percent calculation
        exports_percent = 100 * (exports - baseline_exports) / exports
        
        # Create plot
        fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

        # Determine bar colors based on EU membership
        bar_colors = ['darkblue' if country in eu_countries else 'orange' for country in exports_percent.index]
        
        # Plot bars with colors
        bars = ax.bar(exports_percent.index, exports_percent.value, color=bar_colors)

        plt.xticks(rotation=45, ha='right')
                
        # Remove default x-tick labels
        ax.set_xticklabels([''])

        # Add labels on top of bars
        countrynames = f.get_country_list()
        countrynames.remove("NOR")  # Remove a specific country by name

        ax.bar_label(ax.containers[0],
                     labels=countrynames,
                     rotation=90,
                     label_type='edge',
                     padding=5,
                     zorder=10,
                     fontsize=15)

        # Adjust y-axis limits to fit text, increasing the upper limit by 10%
        max_height = max([bar.get_height() for bar in bars])
        min_height = min([bar.get_height() for bar in bars])
        ax.set_ylim(min_height - 15, max_height + 15)
    
        # Remove x-axis labels
        ax.set_xticks([])

        # Set y-axis label
        ax.set_ylabel('Exports to all countries (in % change)', fontsize=25)

        # Adjust x-axis limits to fit the bars snugly
        ax.set_xlim([-0.5, len(bars) - 0.5])
    
        # Create custom legend
        eu_patch = mpatches.Patch(color='darkblue', label='EU Countries')
        non_eu_patch = mpatches.Patch(color='orange', label='Non-EU Countries')
        ax.legend(handles=[eu_patch, non_eu_patch], fontsize=15)

        # Set the title with sector name instead of sector code
        sector_name = reverse_lookup.get(sec, "Unknown Sector")
        plt.tight_layout()
        #    plt.show()
        plt.savefig(f'{save_path}exports_{config_name}_{sector_name}.{save_format}', format=save_format)




# =============================================================================
#     for config_name, sol in solutions.items():
#         trade=sol.iot.groupby(['row_country','row_sector','col_country']).sum()+sol.cons
#         trade=trade.query('row_country!=col_country') #dropped those rows for domestic trade
#         exports=trade.loc['NOR',sec,:]
# 
#     
#         #percent calculation
#         exports_percent=100*(exports-baseline_exports)/exports
# 
#         # Create plot
#         fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)
# 
#         # Plot bars with colors
#         bars = ax.bar(exports_percent.index, exports_percent.value)
# 
#         plt.xticks(rotation=45, ha='right')
#                 
#         # Remove default x-tick labels
#         ax.set_xticklabels([''])
# 
#         # Add labels on top of bars
#         countrynames = f.get_country_list()
#         # Remove a specific country by name
#         countrynames.remove("NOR")
# 
#         # Add labels on top of bars
#         ax.bar_label(ax.containers[0],
#                      labels=countrynames,
#                      rotation=90,
#                      label_type='edge',
#                      padding=5,
#                      zorder=10,
#                      fontsize=15)
# 
#         # Adjust y-axis limits to fit text, increasing the upper limit by 10%
#         max_height = max([bar.get_height() for bar in bars])
#         min_height = min([bar.get_height() for bar in bars])
#         ax.set_ylim(min_height - 15, max_height + 15)
#         
#         
#         # Remove x-axis labels
#         ax.set_xticks([])
# 
#     
#         # Set y-axis label
#         ax.set_ylabel('Exports to all countries (in % change)', fontsize=25)
# 
#         # Adjust x-axis limits to fit the bars snugly
#         ax.set_xlim([-0.5, len(bars) - 0.5])
# 
#         # Adjust axis limits to fit text, increasing the upper limit by 10%
#         #y_max = max(exports.value)
#         #ax.set_ylim([min(exports.value) - 3, y_max * 1.1])
#         #ax.set_xlim([-1, len(sectors)])
# 
#         # Set the title with sector name instead of sector code
#         sector_name = reverse_lookup.get(sec, "Unknown Sector")
#         #plt.title(f'{config_name} - {sector_name}', fontsize=25)
#         plt.tight_layout()
# 
#         plt.savefig(f'{save_path}exports_{config_name}_{sector_name}.{save_format}', format=save_format)
#         #plt.show()
# 
# =============================================================================



#%% Norway vs other countries - Prices and exports

#THIS IS MEANINGLESS - AVERAGE DOES NOT MAKE ANY SENSE

#plot this like price graph/country graph
pavg=sol.price.groupby(['row_country']).mean()

# Define the list of EU countries
eu_countries = {'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 
                'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 
                'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'}

countrynames = f.get_country_list()

from configurations import sector_classification, sector_colors


for config_name, sol in solutions.items():
    pavg=sol.price.groupby(['row_country']).mean()
    
    #Create a dictionary to map each sector to its PrimarySecondary category
    #sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    #colors = []

    #for sector in sectors:
    #    if sector in sector_to_primary_secondary:
    #        primary_secondary = sector_to_primary_secondary[sector]
    #        colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
    #    else:
    #        colors.append('gray')  # Default color for sectors not categorized

    # Determine bar colors based on EU membership
    bar_colors = ['darkblue' if country in eu_countries else 'orange' for country in exports_percent.index]
        
    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(countrynames, pavg.hat * 100 - 100, color=bar_colors)

    # Remove default x-tick labels
    ax.set_xticklabels([''])

    # Add labels on top of bars
    ax.bar_label(ax.containers[0],
                 labels=countrynames,
                 rotation=90,
                 label_type='edge',
                 padding=5,
                 zorder=10,
                 fontsize=15)

    # Set y-axis label
    ax.set_ylabel('Price change in %', fontsize=25)

    # Adjust axis limits to fit text
    ax.set_ylim([min(pavg.hat* 100 - 100) - 3, max(pavg.hat* 100 - 100) + 3])
    ax.set_xlim([-1, len(countrynames)])

    #plt.title(f'{config_name}', fontsize=25)
    #plt.savefig(f'{save_path}sectors_prices_{config_name}.{save_format}', format=save_format)
    plt.show()

#Norway is in the middle - not particularly high price increase, not particularly low




#%%other graphs



#real income change and gdp by country?
#only world gdp
