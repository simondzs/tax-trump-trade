#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 18:01:10 2024

@author: dora
"""

import funcs_for_dora as f
import matplotlib.pyplot as plt
from configurations import configurations, sector_classification, sector_colors
import pandas as pd
import matplotlib.patches as mpatches

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
            results_path=f'results_dora/{config["name"]}_results.csv', 
            tax_matrix_path=f'results_dora/{config["name"]}_tax_matrix.csv', 
#            results_path=f'results_dora/fgo/{config["name"]}_results.csv', 
#            tax_matrix_path=f'results_dora/fgo/{config["name"]}_tax_matrix.csv', 
#            results_path=f'results_dora/rescaled4agg2/{config["name"]}_results.csv', 
#            tax_matrix_path=f'results_dora/rescaled4agg2/{config["name"]}_tax_matrix.csv', 
            baseline=baseline, 
            data_path='data/',
            eta_path="cp_estimate_allyears.csv", 
            sigma_path="cp_estimate_allyears.csv"
#            eta_path="fgo_estimate.csv", 
#            sigma_path="fgo_estimate.csv"
#            eta_path="rescaled_to_4elasticities_agg2.csv", 
#            sigma_path="rescaled_to_4elasticities_agg2.csv"
            )
    sol.compute_solution(baseline)
    solutions[config["name"]] = sol


# All ICIO data is in mn USD

#%% Setup
import os
# Define paths
elasticities_path = 'cp_estimate_allyears' 
# elasticities_path = 'uniform_elasticities_4'
#elasticities_path = 'rescaled_to_4elasticities_agg2'
#elasticities_path = 'fgo_estimate'
# options are 'cp_estimate_allyears.csv' (Caliendo) or 'uniform_elasticities_4.csv' or 'rescaled_to_4elasticities_agg2.csv' (Fontagne)

save_path = f'output/{elasticities_path}/maingraphs/'
save_format = 'pdf'
def make_directory(path):
    try:
        os.mkdir(path)
    except:
        pass
make_directory(save_path)


#%% Baseline Graph

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

# Get baseline exports
# =============================================================================
# baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
# baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
# baseline_trade=baseline_trade.groupby(['row_country', 'row_sector']).sum()
# baseline_exports=baseline_trade.loc['NOR',:,:]
# 
# =============================================================================

baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade

baseline_trade_toNO=baseline_trade.loc['NOR',:,:]
baseline_trade_toall=baseline_trade_toNO.groupby(['row_sector']).sum()

baseline_trade_toUS = baseline_trade_toNO.xs('USA', level='col_country')

total_trade_toall=baseline_trade_toall.sum()
total_trade_toUS=baseline_trade_toUS.sum()

percent_trade_toall = 100*baseline_trade_toall/total_trade_toall
percent_trade_toUS = 100*baseline_trade_toUS/total_trade_toUS

#graph

# Sectors to be labeled
sectors_to_label = ['fishing', 'mining, energy']

# Ensure the indices of both DataFrames are aligned for the scatter plot
aligned_all, aligned_us = percent_trade_toall.align(percent_trade_toUS, join='inner')

# Create the scatter plot with dots for all sectors
plt.figure(figsize=(10, 8))
plt.scatter(aligned_all, aligned_us, color='blue')

# Plot specific sectors with both dot and label
for i, sector_name in enumerate(sectors):
    if sector_name.lower() in sectors_to_label:
        plt.scatter(aligned_all.iloc[i], aligned_us.iloc[i], color='blue')  # Highlight with a different color if needed
        plt.text(aligned_all.iloc[i], aligned_us.iloc[i], sector_name, fontsize=9, ha='right')

# Adding labels and title
plt.xlabel('Export shares to all countries')
plt.ylabel('Export shares to the US')

# Add a diagonal line y=x for reference
plt.plot([aligned_all.min(), aligned_all.max()], [aligned_all.min(), aligned_all.max()], color='red', linestyle='--')

plt.savefig(save_path+'baseline_exports.pdf',format=save_format)

plt.show()

#%% Baseline excluded


sectors = f.get_sector_names_list()
sector_codes = f.get_sector_list()


# Sectors to exclude
sectors_to_exclude = ['03', '05T06']  # Assuming these codes correspond to fishing and mining, energy

# Create a mapping from sector code to sector name
sector_mapping = {code: name for code, name in zip(sector_codes, sectors)}

# Filter the sectors to exclude
filtered_sectors = [sector for sector in aligned_all.index if sector not in sectors_to_exclude]

# Align the data based on the filtered sectors
filtered_aligned_all = aligned_all.loc[filtered_sectors]
filtered_aligned_us = aligned_us.loc[filtered_sectors]

# Create the plot
plt.figure(figsize=(10, 8))

# Plot each sector name at the corresponding data point
for sector_code in filtered_sectors:
    sector_name = sector_mapping.get(sector_code, sector_code)  # Get the sector name from mapping
    x = filtered_aligned_all.loc[sector_code]
    y = filtered_aligned_us.loc[sector_code]
    plt.scatter(x, y, color='blue')
    plt.text(x, y, sector_name, fontsize=9, ha='right')

# Adding labels and title
plt.xlabel('Export shares to all countries')
plt.ylabel('Export shares to the US')

# Add a diagonal line y=x for reference
plt.plot([filtered_aligned_all.min(), filtered_aligned_all.max()], 
         [filtered_aligned_all.min(), filtered_aligned_all.max()], color='red', linestyle='--')

plt.savefig(save_path+'baseline_exports_nofishmin.pdf', format=save_format)

plt.show()



#%% Pie chart

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade

baseline_trade_toNO=baseline_trade.loc['NOR',:,:]
baseline_trade_toall=baseline_trade_toNO.groupby(['row_sector']).sum()


# Assuming baseline_trade_toall is a Series with sectors as the index and trade values as the data
# You might want to sort the sectors by trade value for better visualization
baseline_trade_toall_sorted = baseline_trade_toall.sort_values(ascending=False, by='value')

# Create a pie chart

# Create a dictionary mapping sector codes to sector names
sector_code_to_name = {code: name for code, name in zip(baseline_trade_toall.index, sectors)}

# Sort baseline_trade_toall by values in descending order
baseline_trade_toall_sorted = baseline_trade_toall.sort_values(by='value', ascending=False)

# Calculate percentage share
total_trade = baseline_trade_toall_sorted['value'].sum()
percentage_share = (baseline_trade_toall_sorted['value'] / total_trade) * 100

# Identify sectors with a share less than 2% and group them under "Others"
threshold = 2.0
small_sectors = percentage_share[percentage_share < threshold].index

# Group small sectors under "Others"
if len(small_sectors) > 0:
    # Sum up the values for small sectors
    small_sectors_sum = baseline_trade_toall_sorted.loc[small_sectors].sum()
    # Create a DataFrame for "Others"
    others_df = pd.DataFrame({'value': [small_sectors_sum]}, index=['Others'])
    
    # Drop small sectors and concatenate with "Others"
    baseline_trade_toall_grouped = pd.concat([
        baseline_trade_toall_sorted.drop(small_sectors),
        others_df
    ])
    
    # Create sector names list
    sector_names_grouped = [sector_code_to_name.get(code, code) for code in baseline_trade_toall_grouped.index]
else:
    baseline_trade_toall_grouped = baseline_trade_toall_sorted
    sector_names_grouped = [sector_code_to_name.get(code, code) for code in baseline_trade_toall_grouped.index]

# Create a pie chart with the grouped sectors
plt.figure(figsize=(10, 8))
plt.pie(baseline_trade_toall_grouped['value'], labels=sector_names_grouped, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.4), pctdistance=0.85)

# Adjust the position of labels to avoid overlap
plt.tight_layout()

# Adding a title
#plt.title('Distribution of Baseline Trade to All Countries by Sector')

plt.savefig(save_path+'baseline_exports_pie.pdf',format=save_format)

plt.show()

# Identify sector names of small sectors
small_sector_names = [sector_code_to_name.get(code, code) for code in small_sectors]

# =============================================================================
# # Display the list of sector names for the small sectors
# print("Sector names of small sectors:")
# for name in small_sector_names:
#     print(name)
# 
# =============================================================================

# =============================================================================
# IT
# Administration
# Water transport
# Machinery
# Tourism
# Warehousing
# Transport equipment
# Telecom
# Manufacturing nec
# Energy
# Fabricated metals
# Electrical equipment
# Pharmaceuticals
# Electronics
# Media
# Mining, non-energy
# Paper
# Non-metallic minerals
# Entertainment
# Plastics
# Post
# Textiles
# Real estate
# Agriculture
# Education
# Wood
# Health
# Construction
# Other service
# Water supply
# Public sector
# 
# =============================================================================
#%% AGGREGATE GRAPHS - TODO: change order of scenarios

#%% Output on and offshore for each scenario

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

# Specify the desired order of scenarios
desired_order = ['Baseline','US10', 'US1060', 'US1060EU0', 'US2060','US10Retal', 'US1060Retal', 
                 'US1060EU0Retal', 'US2060Retal', 'US10Sectors','US10SectorsRetal']

# Reorder sumsoutput_df based on the desired order
sumsoutput_df = sumsoutput_df.loc[desired_order]

# Plot stacked bar chart
#ax[0,0].plt.figure(figsize=(10, 6))
sumsoutput_df.plot(kind='bar', stacked=True, color=['blue', 'orange'], ax=plt.gca())  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, key in enumerate(desired_order):
    if key != 'Baseline':
        value=totaloutput[key]
        plt.text(i, value + 0.05 * max(totaloutput.values()), f'{percent_changes_output[key]:.1f}%', ha='center')

# Adjust y-axis limits to make space for text annotations
max_output = max(totaloutput.values())
plt.ylim(0, max_output + 0.08 * max_output)  # Adjust as needed for spacing


# Get current axis
ax = plt.gca()

# Adjust y-axis tick labels to show values in billions and get tick positions
yticks = ax.get_yticks()

# Adjust y-axis tick labels to show values in billions
ax.set_yticks(ax.get_yticks())  # Set the positions of the ticks
ax.set_yticklabels([f'{int(tick / 1000)}' for tick in ax.get_yticks()])  # Set the labels


plt.ylabel('Nominal Output in bn USD (2018)')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(save_path+'scenarios_output.pdf',format=save_format)
plt.show()



#%% GDP on and offshore for each scenario

# Example baseline data (replace with your actual data and access method)
#baseline_gdp = baseline.cons.loc['NOR', :, 'NOR']  # Dropping imports
#baseline_gdp = baseline_gdp.sum().sum()  # Ensure baseline_gdp is a scalar value by summing over all axes


baseline_gdp=baseline.va.groupby(['col_country']).sum().loc['NOR'].values[0]

#408673

#baseline_gdp=baseline.cons.groupby(['col_country']).sum()
#baseline_gdp=baseline_gdp.loc['NOR']
#baseline_gdp=baseline_gdp.loc['NOR']-baseline.deficit.loc['NOR']

#408672


# For percent calculation
tot_gdp = baseline_gdp

# Calculate the sum of 'variable1' for each scenario
sumsgdp = {}
totalgdp = {}

# Add baseline output to sumsoutput with a unique key
sumsgdp['Baseline'] = baseline_gdp
totalgdp['Baseline'] = tot_gdp

for config_name, sol in solutions.items():
    #sol_gdp = sol.cons.loc['NOR', :, 'NOR']  # Select data
    #sol_gdp = sol_gdp.sum().sum()  # Ensure sol_gdp is reduced to a scalar value
    
    sol_gdp=sol.va.groupby(['col_country']).sum().loc['NOR'].values[0]

    
    summed_gdp = sol_gdp
    sumsgdp[config_name] = summed_gdp
    
    # For percent calculation
    totalgdp[config_name] = sol_gdp

# Calculate percent change relative to baseline
baseline_total = totalgdp['Baseline']
percent_changes_gdp = {}
for key, value in totalgdp.items():
    if key == 'Baseline':
        percent_changes_gdp[key] = 0.0  # Baseline itself has 0% change
    else:
        percent_change = ((value - baseline_total) / baseline_total) * 100
        percent_changes_gdp[key] = percent_change

# Convert sumsoutput dictionary to DataFrame with index
sumsgdp_df = pd.DataFrame(list(sumsgdp.items()), columns=['Scenario', 'GDP']).set_index('Scenario')

# Specify the desired order of scenarios
desired_order = ['Baseline', 'US10', 'US1060', 'US1060EU0', 'US2060', 'US10Retal', 'US1060Retal', 
                 'US1060EU0Retal', 'US2060Retal', 'US10Sectors', 'US10SectorsRetal']

# Reorder sumsoutput_df based on the desired order
sumsgdp_df = sumsgdp_df.loc[desired_order]

# Plot stacked bar chart
sumsgdp_df.plot(kind='bar', stacked=True, color=['blue', 'orange'], ax=plt.gca())  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, key in enumerate(desired_order):
    if key != 'Baseline':
        # Get the height of the current bar (gdp value) - ensure it's a scalar
        gdp_value = totalgdp[key]  # This should now be a single numeric value
        
        # Add text at the top of the bar with percent change
        plt.text(i, gdp_value + 0.05 * max(totalgdp.values()),  # Adjust the y-coordinate for spacing
                 f'{percent_changes_gdp[key]:.1f}%', ha='center', va='bottom', fontsize=10, color='black')

# Adjust y-axis limits to make space for text annotations
max_gdp = max(totalgdp.values())
plt.ylim(0, max_gdp + 0.1 * max_gdp)  # Adjust as needed for spacing

# Get current axis
ax = plt.gca()

# Adjust y-axis tick labels to show values in billions and get tick positions
yticks = ax.get_yticks()

# Adjust y-axis tick labels to show values in billions
ax.set_yticks(ax.get_yticks())  # Set the positions of the ticks
ax.set_yticklabels([f'{int(tick / 1000)}' for tick in ax.get_yticks()])  # Set the labels

plt.ylabel('Nominal GDP in bn USD (2018)')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(save_path+'scenarios_gdp.pdf',format=save_format)
plt.show()




#%% Exports onshore offshore for each scenario 

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


# Specify the desired order of scenarios
desired_order = ['Baseline','US10', 'US1060', 'US1060EU0', 'US2060','US10Retal', 'US1060Retal', 
                 'US1060EU0Retal', 'US2060Retal', 'US10Sectors','US10SectorsRetal']

# Reorder sumsoutput_df based on the desired order
sumtrade_df = sumtrade_df.loc[desired_order]

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
#plt.figure(figsize=(10, 6))
sumtrade_df .plot(kind='bar', stacked=True, color=['blue', 'orange'], ax=plt.gca())  # Adjust colors as needed

# Adding percent change as text on top of bars
for i, key in enumerate(desired_order):
    if key != 'Baseline':
        value=tottrade[key]
        #plt.text(i, 100*(value-total_baseline_trade)/value, f'{percent_changes[key]:.1f}%', ha='center')
        plt.text(i, value + 0.05 * max(tottrade.values()), f'{percent_changes_trade[key]:.1f}%', ha='center')

# Adjust y-axis limits to make space for text annotations
max_output = max(tottrade.values())
plt.ylim(0, max_output + 0.08 * max_output)  # Adjust as needed for spacing

# Get current axis
ax = plt.gca()

# Adjust y-axis tick labels to show values in billions and get tick positions
yticks = ax.get_yticks()

# Adjust y-axis tick labels to show values in billions
ax.set_yticks(ax.get_yticks())  # Set the positions of the ticks
ax.set_yticklabels([f'{int(tick / 1000)}' for tick in ax.get_yticks()])  # Set the labels


plt.ylabel('Total Nominal Exports in bn USD (2018)') #TODO: Check if this is really bn
#plt.title('Stacked Bar Chart of Exports by Scenario and Onshore vs Offshore')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(save_path+'scenarios_exports.pdf',format=save_format)
plt.show()


#%% Labor reallocation by off and onshore for each scenario

#Problem: There is no labor for baseline
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

# Specify the desired order of scenarios
desired_order = ['US10', 'US1060', 'US1060EU0', 'US2060','US10Retal', 'US1060Retal', 
                 'US1060EU0Retal', 'US2060Retal', 'US10Sectors','US10SectorsRetal']

# Reorder sumsoutput_df based on the desired order
sumlabor_df = sumlabor_df.loc[desired_order]

# Create the plot
fig, ax = plt.subplots()

# Plot stacked bar chart
sumlabor_df.plot(kind='bar', stacked=True, ax=ax,zorder=2, color=['blue', 'orange'])  # Adjust colors as needed

# Now retrieve y-tick values and add horizontal lines at those positions
y_ticks = ax.get_yticks()  # Get the y-ticks after plotting the bars
for y in y_ticks:
    ax.axhline(y=y, color='gray', linestyle='--', linewidth=1, zorder=0)  # zorder=0 to place in background


plt.ylabel('Labor reallocation in percent')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='lower right')
plt.tight_layout()

plt.savefig(save_path+'scenarios_labor.pdf',format=save_format)
plt.show()




#%% Utility

utility={}
for config_name, sol in solutions.items():

    #utility changes for Norway
    utility[config_name] = 100*(sol.utility.loc['NOR']-1)
    

# Convert sumsoutput dictionary to DataFrame and transpose it
utility_df = pd.DataFrame(utility).T

# Specify the desired order of scenarios
desired_order = ['US10', 'US1060', 'US1060EU0', 'US2060','US10Retal', 'US1060Retal', 
                 'US1060EU0Retal', 'US2060Retal', 'US10Sectors','US10SectorsRetal']

# Reorder sumsoutput_df based on the desired order
utility_df = utility_df.loc[desired_order]

# Create the plot
fig, ax = plt.subplots()

# Plot stacked bar chart first
utility_df.plot(kind='bar', stacked=True, ax=ax, zorder=2)  # zorder=2 to place bars in foreground

# Now retrieve y-tick values and add horizontal lines at those positions
y_ticks = ax.get_yticks()  # Get the y-ticks after plotting the bars
for y in y_ticks:
    ax.axhline(y=y, color='gray', linestyle='--', linewidth=1, zorder=0)  # zorder=0 to place in background

# Customize labels and layout
ax.set_ylabel('Real income change (in percent)')
ax.set_xticks(range(len(utility_df.index)))
ax.set_xticklabels(utility_df.index, rotation=45, ha='right')

plt.tight_layout()
plt.legend().remove()

plt.savefig(save_path + 'scenarios_utility.pdf', format=save_format)
plt.show()




#%% SECTORAL GRAPHS

#%% Output sector graph

import matplotlib.pyplot as plt

# Get sector list and labor reallocation data
sectors = f.get_sector_names_list()

# Get baseline output
baseline_output = baseline.output.loc['NOR', :]

for config_name, sol in solutions.items():
    output = sol.output.loc['NOR', :]
    
    # Create a dictionary to map each sector to its PrimarySecondary category
    sector_to_primary_secondary = {sector: info['PrimarySecondary'] for sector, info in sector_classification.items()}

    colors = []

    for sector in sectors:
        if sector in sector_to_primary_secondary:
            primary_secondary = sector_to_primary_secondary[sector]
            colors.append(sector_colors.get(primary_secondary, 'gray'))  # Default to 'gray' if category not found
        else:
            colors.append('gray')  # Default color for sectors not categorized

    # Percent calculation
    output_percent = 100 * (output - baseline_output) / baseline_output

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, output.value, color=colors)

    plt.xticks(rotation=45, ha='right', fontsize=20)
    
    # Add percent_output on top of the bars with conditional coloring
    for bar, percent in zip(bars, output_percent.value):
        height = bar.get_height()
        color = 'green' if percent >= 0 else 'red'
        ax.annotate(
            f'{percent:.1f}%',  # Format the percentage with 1 decimal place
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            rotation=90,
            fontsize=15,
            color=color  # Set the color based on percent value
        )

    # Set y-axis label
    ax.set_ylabel('Nominal Output (mn USD 2018)', fontsize=25)

    # Adjust axis limits to fit text, increasing the upper limit by 10%
    y_max = max(output.value)
    ax.set_ylim([min(output.value) - 3, y_max * 1.1])
    ax.set_xlim([-1, len(sectors)])

    # Set the plot title
    #plt.title(f'{config_name}', fontsize=25)

    # Save or show the plot
    plt.savefig(f'{save_path}sectors_output_{config_name}.{save_format}', format=save_format)
    plt.show()






#%% Real output sector graph

#Todo: make font size larger for labels

#from configurations import sector_classification, sector_colors

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
    
    # Set y-axis label
    ax.set_ylabel('Change in Real Output (in %)', fontsize=25)
    
    # Add labels on top of bars
    ax.bar_label(ax.containers[0],
                 labels=sectors,
                 rotation=90,
                 label_type='edge',
                 padding=5,
                 zorder=10,
                 fontsize=20)


    # Adjust axis limits to fit text
    ax.set_ylim([min(output_hat.value) - 7, max(output_hat.value) + 7])
    ax.set_xlim([-1, len(sectors)])


    
    # Add horizontal lines at every tick
    y_ticks = ax.yaxis.get_majorticklocs()  # Get the y-tick locations
    for y in y_ticks:
        ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, zorder=0)  # Draw horizontal lines


    # Remove default x-tick labels
    ax.set_xticklabels([''])

    # Bring the bars to the front
    for bar in bars:
        bar.set_zorder(1)

    #plt.title(f'{config_name}', fontsize=25)
    plt.savefig(f'{save_path}sectors_real_output_{config_name}.{save_format}', format=save_format)
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
                 fontsize=20)

    # Set y-axis label
    ax.set_ylabel('Labor reallocation (% of workforce)', fontsize=25)

    # Adjust axis limits to fit text
    ax.set_ylim([min(y.value * 100 - 100) - 7, max(y.value * 100 - 100) + 7])
    ax.set_xlim([-1, len(sectors)])

    # Add horizontal lines at every tick
    y_ticks = ax.yaxis.get_majorticklocs()  # Get the y-tick locations
    for y in y_ticks:
        ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, zorder=0)  # Draw horizontal lines

    # Bring the bars to the front
    for bar in bars:
        bar.set_zorder(1)

    #plt.title(f'{config_name}', fontsize=25)
    plt.savefig(f'{save_path}sectors_labor_{config_name}.{save_format}', format=save_format)
    plt.show()




#%% Export sector graph

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
    exports_percent=100*(exports-baseline_exports)/baseline_exports

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, exports.value, color=colors)

    plt.xticks(rotation=45, ha='right', fontsize=20)
    
    # Add percent_output on top of the bars
    for bar, percent in zip(bars, exports_percent.value):
        height = bar.get_height()
        color = 'green' if percent >= 0 else 'red'
        ax.annotate(
            f'{percent:.1f}%',  # Format the percentage with 2 decimal places
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            rotation=90,
            fontsize=15,
            color=color  # Set the color based on percent value
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
    imports_percent=100*(imports-baseline_imports)/baseline_imports

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, imports.value, color=colors)

    plt.xticks(rotation=45, ha='right', fontsize=20)
    
    # Add percent_output on top of the bars
    for bar, percent in zip(bars, imports_percent.value):
        height = bar.get_height()
        color = 'green' if percent >= 0 else 'red'
        ax.annotate(
            f'{percent:.1f}%',  # Format the percentage with 2 decimal places
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            rotation=90,
            fontsize=15,
            color=color  # Set the color based on percent value
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
    exports_percent=100*(exports-baseline_exports)/baseline_exports

    # Create plot
    fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

    # Plot bars with colors
    bars = ax.bar(sectors, exports.value, color=colors)

    plt.xticks(rotation=45, ha='right', fontsize=20)
    
    # Add percent_output on top of the bars
    for bar, percent in zip(bars, exports_percent.value):
        height = bar.get_height()
        color = 'green' if percent >= 0 else 'red'
        ax.annotate(
            f'{percent:.1f}%',  # Format the percentage with 2 decimal places
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            rotation=90,
            fontsize=15,
            color=color
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

#%% Global utility change

# =============================================================================
# globalutility={}
# 
# 
# for config_name, sol in solutions.items():
#     
#     #utility changes for Norway
#     globalutility[config_name] = 100*(sol.utility-1)
# #    globalutility[config_name] = (sol.utility)
# 
# # Combine all scenarios into one DataFrame
# combined_df = pd.concat(globalutility.values(), axis=1, keys=globalutility.keys())
# 
# # The DataFrame's columns are now a MultiIndex with scenarios on the first level
# combined_df.columns = combined_df.columns.droplevel(1)  # Drop the 'Change in Utility' sub-level
# 
# # Reset the index to bring 'Country' back as a column
# combined_df = combined_df.reset_index()
# 
# # Rename the 'index' column to 'Country' if necessary
# combined_df = combined_df.rename(columns={'index': 'country'})
# 
# # Plotting the bar chart
# combined_df.plot(x='country', kind='bar', figsize=(10, 6))
# 
# # Adding labels and title
# plt.ylabel('Change in Utility')
# plt.title('Change in Utility by Country for Different Scenarios')
# plt.xticks(rotation=90)
# plt.legend(title='Scenario')
# 
# # Show the plot
# plt.tight_layout()
# plt.show()
# 
# =============================================================================


#%% Global utility change

from configurations import EUcountries


globalutility={}


for config_name, sol in solutions.items():
    
    #utility changes for Norway
    globalutility[config_name] = 100*(sol.utility-1)
#    globalutility[config_name] = (sol.utility)

# Combine all scenarios into one DataFrame
combined_df = pd.concat(globalutility.values(), axis=1, keys=globalutility.keys())

# The DataFrame's columns are now a MultiIndex with scenarios on the first level
combined_df.columns = combined_df.columns.droplevel(1)  # Drop the 'Change in Utility' sub-level

# Reset the index to bring 'Country' back as a column
combined_df = combined_df.reset_index()

# Rename the 'index' column to 'Country' if necessary
combined_df = combined_df.rename(columns={'index': 'country'})

# Manually define the groups of scenarios you want to plot together
scenario_groups = [
    ['US10', 'US1060', 'US1060EU0', 'US2060'],  # Group 1
    ['US10Retal', 'US1060Retal','US1060EU0Retal', 'US2060Retal'],               # Group 2
    ['US10Sectors', 'US10SectorsRetal']   # Group 3
    # Add more groups as needed
]

# Extract non-EU countries and sort them alphabetically
non_eu_countries = sorted([country for country in combined_df['country'] if country not in EUcountries])

# Combine EU and non-EU countries
ordered_countries = EUcountries + non_eu_countries

# Reorder the DataFrame
combined_df['country'] = pd.Categorical(combined_df['country'], categories=ordered_countries, ordered=True)
combined_df = combined_df.sort_values('country')

# Find the index position for the last EU country
last_eu_country_index = len(EUcountries) - 1

# Loop through each group and create a plot
for i, group in enumerate(scenario_groups):
    # Create a subset of the combined DataFrame for the current group of scenarios
    combined_df_subset = combined_df[['country'] + group]
    
    # Plotting the bar chart for the current subset
    combined_df_subset.plot(x='country', kind='bar', figsize=(10, 6))
    
    # Adding labels and title
    plt.ylabel('Change in Real Income (in %)')
#    plt.title(f'Change in Utility by Country for Scenarios {", ".join(group)}')
    plt.xticks(rotation=90)
    plt.legend(title='Scenario')
    
    
    # Add a vertical line after the last EU country
    plt.axvline(x=last_eu_country_index + 0.5, color='black', linestyle='--')

    # Drop the x-axis label
    plt.xlabel('')  
    
    # Show the plot
    plt.tight_layout()
    plt.savefig(f'{save_path}utility-{"-".join(group)}.{save_format}', format=save_format)
    plt.show()



#%% COUNTRY GRAPHS
# =============================================================================
# #THIS TAKES A FEW MINUTES TO RUN
# #Here, we need a graph for each sector by country.
# 
# 
# save_path = f'output/{elasticities_path}/country_sector_graphs/'
# 
# 
# # Get sector list
# sectors = f.get_sector_list()
# # Create reverse lookup dictionary for sector names
# reverse_lookup = {v['SectorCode']: k for k, v in sector_classification.items()}
# 
# 
# baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
# baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
# # Define the list of EU countries
# eu_countries = {'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 
#                 'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 
#                 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'}
# 
# 
# #sec='01T02'
# 
# for sec in sectors:
# 
#     # Get baseline exports
#     baseline_exports=baseline_trade.loc['NOR',sec,:]
# 
#     for config_name, sol in solutions.items():
#         trade = sol.iot.groupby(['row_country', 'row_sector', 'col_country']).sum() + sol.cons
#         trade = trade.query('row_country != col_country')  # dropped those rows for domestic trade
#         exports = trade.loc['NOR', sec, :]
# 
#         # Percent calculation
#         exports_percent = 100 * (exports - baseline_exports) / baseline_exports
#         
#         # Create plot
#         fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)
# 
#         # Determine bar colors based on EU membership
#         bar_colors = ['darkblue' if country in eu_countries else 'orange' for country in exports_percent.index]
#         
#         # Plot bars with colors
#         bars = ax.bar(exports_percent.index, exports_percent.value, color=bar_colors)
# 
#         plt.xticks(rotation=45, ha='right', fontsize=20)
# 
#         # Remove default x-tick labels
#         ax.set_xticklabels([''])
# 
#         # Add labels on top of bars
#         countrynames = f.get_country_list()
#         countrynames.remove("NOR")  # Remove a specific country by name
# 
#         ax.bar_label(ax.containers[0],
#                      labels=countrynames,
#                      rotation=90,
#                      label_type='edge',
#                      padding=5,
#                      zorder=10,
#                      fontsize=20)
# 
#         # Adjust y-axis limits to fit text, increasing the upper limit by 10%
#         max_height = max([bar.get_height() for bar in bars])
#         min_height = min([bar.get_height() for bar in bars])
#         ax.set_ylim(min_height - 15, max_height + 15)
#     
#         # Remove x-axis labels
#         ax.set_xticks([])
# 
#         # Set y-axis label
#         ax.set_ylabel('Exports to all countries (in % change)', fontsize=25)
# 
#         # Adjust x-axis limits to fit the bars snugly
#         ax.set_xlim([-1, len(bars) + 0.3])
# 
#         # Add horizontal lines at every tick
#         y_ticks = ax.yaxis.get_majorticklocs()  # Get the y-tick locations
#         for y in y_ticks:
#             ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, zorder=0)  # Draw horizontal lines
# 
#         # Bring the bars to the front
#         for bar in bars:
#             bar.set_zorder(1)
#     
#         # Create custom legend
#         eu_patch = mpatches.Patch(color='darkblue', label='EU Countries')
#         non_eu_patch = mpatches.Patch(color='orange', label='Non-EU Countries')
#         ax.legend(handles=[eu_patch, non_eu_patch], fontsize=15)
# 
#         # Set the title with sector name instead of sector code
#         sector_name = reverse_lookup.get(sec, "Unknown Sector")
#         plt.tight_layout()
#         #    plt.show()
#         plt.savefig(f'{save_path}exports_{config_name}_{sector_name}.{save_format}', format=save_format)
# 
# =============================================================================






#%% Real exports by country

#THIS TAKES A FEW MINUTES TO RUN
#Here, we need a graph for each sector by country.

import matplotlib.lines as mlines

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


sec='24'
config_name='US10Sectors'
sol=solutions[config_name]
for sec in sectors:

    # Get baseline exports
    baseline_exports=baseline_trade.loc['NOR',sec,:]

    for config_name, sol in solutions.items():
        trade = sol.iot.groupby(['row_country', 'row_sector', 'col_country']).sum() + sol.cons
        trade = trade.query('row_country != col_country')  # dropped those rows for domestic trade
        exports = trade.loc['NOR', sec, :]

        # Percent calculation
        exports_percent = 100 * (exports - baseline_exports) / baseline_exports
             
        #real_exports_percent = 100*(1-(baseline_exports/exports)*sol.price.loc['NOR', sec].hat)
        real_exports_percent = 100*(exports-baseline_exports)/baseline_exports*sol.price.loc['NOR', sec].hat

        # Create plot
        fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)

        # Determine bar colors based on EU membership
        bar_colors = ['darkblue' if country in eu_countries else 'orange' for country in real_exports_percent.index]
        
        # Plot bars with colors
        bars = ax.bar(real_exports_percent.index, real_exports_percent.value, color=bar_colors)

        plt.xticks(rotation=45, ha='right', fontsize=20)
        
        # Add dots for exports_percent
        ax.scatter(real_exports_percent.index, exports_percent, color='red', s=100, zorder=2)


        # Remove default x-tick labels
        ax.set_xticklabels([''])

        # Add labels on top of bars
        countrynames = f.get_country_list()
        countrynames.remove("NOR")  # Remove a specific country by name

        ax.bar_label(ax.containers[0],
                     labels=countrynames,
                     rotation=90,
                     label_type='edge',
                     padding=20,
                     zorder=10,
                     fontsize=20)

        # Adjust y-axis limits to fit text, increasing the upper limit by 10%
        max_height = max([bar.get_height() for bar in bars])
        min_height = min([bar.get_height() for bar in bars])
        ax.set_ylim(min_height - 15, max_height + 15)
        
        
        # Remove x-axis labels
        ax.set_xticks([])

        # Set y-axis label
        ax.set_ylabel('Exports to all countries (in % change)', fontsize=25)

        # Adjust x-axis limits to fit the bars snugly
        ax.set_xlim([-1, len(bars) + 0.3])

        # Add horizontal lines at every tick
        y_ticks = ax.yaxis.get_majorticklocs()  # Get the y-tick locations
        for y in y_ticks:
            ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, zorder=0)  # Draw horizontal lines

        # Bring the bars to the front
        for bar in bars:
            bar.set_zorder(1)
    
        # Create custom legend
        eu_patch = mpatches.Patch(color='darkblue', label='Real Exports EU Countries')
        non_eu_patch = mpatches.Patch(color='orange', label='Real Exports Non-EU Countries')
        dot_patch = mlines.Line2D([], [], color='red', marker='o', linestyle='None', markersize=10, label='Nominal Exports')
        ax.legend(handles=[eu_patch, non_eu_patch, dot_patch], fontsize=15)

        # Set the title with sector name instead of sector code
        sector_name = reverse_lookup.get(sec, "Unknown Sector")
        plt.tight_layout()
        #plt.savefig(f'{save_path}real_exports_{config_name}_{sector_name}.{save_format}', format=save_format)
        plt.show()




#%% Copy country graphs

import shutil

# Source and destination directories
source_dir = f'output/{elasticities_path}/country_sector_graphs/'
destination_dir = f'output/{elasticities_path}/country_sector_graphs/upload/'

# List of keywords to look for in the filenames
keywords = ["Basic metals", "Transport equipment", "Fishing"]  # Add other keywords as needed

# Create the destination directory if it doesn't exist
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# Loop through each keyword and copy the matching PDF files
for keyword in keywords:
    for file_name in os.listdir(source_dir):
        # Check if the file name contains the keyword and is a PDF
        if keyword in file_name and file_name.endswith(".pdf"):
            # Construct full file paths
            source_file = os.path.join(source_dir, file_name)
            destination_file = os.path.join(destination_dir, file_name)
            
            # Copy the file
            shutil.copy2(source_file, destination_file)
            print(f"Copied: {file_name} to {destination_dir}")

print("All matching files have been copied.")


#%% Copy country graphs in folders

import os
import shutil

# Define the path to the folder containing the files
source_folder = 'output/cp_estimate_allyears/country_sector_graphs/'
destination_folder = 'graphs-all-sectors/'

# Iterate over each file in the source folder
for filename in os.listdir(source_folder):
    if filename.endswith('.pdf'):  # Only consider PDF files
        # Debug: Print the filename being processed
        print(f"Processing file: {filename}")
        
        # Ensure the filename follows the expected pattern
        parts = filename.split('_')
        if len(parts) > 2:  # Check that there are enough parts after splitting
            part = parts[2]

            # Debug: Print the part extracted for the folder name
            print(f"Folder part extracted: {part}")

            # Create a new folder with the extracted part if it doesn't exist
            destination_folder2 = os.path.join(destination_folder, part)
            os.makedirs(destination_folder2, exist_ok=True)

            # Copy the file to the new folder
            shutil.copy(os.path.join(source_folder, filename), destination_folder2)

            # Debug: Confirm file copy
            print(f"Copied {filename} to {destination_folder2}")
        else:
            print(f"Skipping file {filename} due to unexpected filename format.")

print("Files have been copied to their respective folders.")

#%%other graphs



#real income change and gdp by country?
#only world gdp





#%%

# =============================================================================
# tradeinermed = sol.iot.groupby(['row_country', 'row_sector', 'col_country']).sum()
# tradeinermed  = tradeinermed.query('row_country != col_country')  # dropped those rows for domestic trade
# tradeinermed=tradeinermed.loc['NOR', '03', :]
# tradefinal =  sol.cons
# tradefinal = tradefinal.query('row_country != col_country')
# tradefinal=tradefinal.loc['NOR', '03', :]
# 
# =============================================================================

#%%

#%% Exports by sector

# =============================================================================
# # Get sector list and labor reallocation data
# sectors = f.get_sector_names_list()
# 
# # Get baseline exports
# baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
# baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
# baseline_trade=baseline_trade.groupby(['row_country', 'row_sector']).sum()
# #baseline_exports=baseline_trade.loc['USA',:,:]
# 
# 
# baseline_exports_transport=baseline_trade.loc[:,'29T30',:]
# percent=baseline_exports_transport/baseline_exports_transport.sum()
# 
# baseline_exports_basicmetals=baseline_trade.loc[:,'24',:]
# percentbm=baseline_exports_basicmetals/baseline_exports_basicmetals.sum()
# 
# #imports
# baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
# baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
# 
# baseline_imports_transport=baseline_trade.loc[:,'29T30','NOR']
# percent=baseline_imports_transport/baseline_imports_transport.sum()
# 
# baseline_imports_basicmetals=baseline_trade.loc[:,'24','NOR']
# percentbm=baseline_imports_basicmetals/baseline_imports_basicmetals.sum()
# 
# =============================================================================
#%% IMport country graphs

# =============================================================================
# #THIS TAKES A FEW MINUTES TO RUN
# #Here, we need a graph for each sector by country.
# 
# import matplotlib.lines as mlines
# 
# save_path = f'output/{elasticities_path}/country_sector_graphs/'
# 
# 
# # Get sector list
# sectors = f.get_sector_list()
# # Create reverse lookup dictionary for sector names
# reverse_lookup = {v['SectorCode']: k for k, v in sector_classification.items()}
# 
# 
# baseline_trade=baseline.iot.groupby(['row_country','row_sector','col_country']).sum()+baseline.cons
# baseline_trade=baseline_trade.query('row_country!=col_country') #dropped those rows for domestic trade
# # Define the list of EU countries
# eu_countries = {'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 
#                 'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 
#                 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'}
# 
# 
# sec='24'
# #config_name='US10'
# for sec in sectors:
# 
#     # Get baseline exports
#     #baseline_exports=baseline_trade.loc['NOR',sec,:]
#     baseline_imports=baseline_trade.loc[:,sec,'NOR']
# 
#     for config_name, sol in solutions.items():
#         print(config_name)
#         trade = sol.iot.groupby(['row_country', 'row_sector', 'col_country']).sum() + sol.cons
#         trade = trade.query('row_country != col_country')  # dropped those rows for domestic trade
#         #exports = trade.loc['NOR', sec, :]
#         imports = trade.loc[:, sec, 'NOR']
# 
#         # Percent calculation
#         #exports_percent = 100 * (exports - baseline_exports) / baseline_exports
#         imports_percent = 100 * (imports- baseline_imports) / baseline_imports
#              
#         #real_exports_percent = 100*(1-(baseline_exports/exports)*sol.price.loc['NOR', sec].hat)
#         #real_exports_percent = 100*(exports-baseline_exports)/baseline_exports*sol.price.loc['NOR', sec].hat
#         real_imports_percent = 100*(imports-baseline_imports)/baseline_imports*sol.price.loc['NOR', sec].hat
# 
#         # Create plot
#         fig, ax = plt.subplots(figsize=(18, 10), constrained_layout=True)
# 
#         # Determine bar colors based on EU membership
#         bar_colors = ['darkblue' if country in eu_countries else 'orange' for country in real_imports_percent.index]
#         
#         # Plot bars with colors
#         bars = ax.bar(real_imports_percent.index, real_imports_percent.value, color=bar_colors)
# 
#         plt.xticks(rotation=45, ha='right', fontsize=20)
#         
#         # Add dots for exports_percent
#         ax.scatter(real_imports_percent.index, imports_percent, color='red', s=100, zorder=2)
# 
# 
#         # Remove default x-tick labels
#         ax.set_xticklabels([''])
# 
#         # Add labels on top of bars
#         countrynames = f.get_country_list()
#         countrynames.remove("NOR")  # Remove a specific country by name
# 
#         ax.bar_label(ax.containers[0],
#                      labels=countrynames,
#                      rotation=90,
#                      label_type='edge',
#                      padding=20,
#                      zorder=10,
#                      fontsize=20)
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
#         # Set y-axis label
#         ax.set_ylabel('Imports to all countries (in % change)', fontsize=25)
# 
#         # Adjust x-axis limits to fit the bars snugly
#         ax.set_xlim([-1, len(bars) + 0.3])
# 
#         # Add horizontal lines at every tick
#         y_ticks = ax.yaxis.get_majorticklocs()  # Get the y-tick locations
#         for y in y_ticks:
#             ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, zorder=0)  # Draw horizontal lines
# 
#         # Bring the bars to the front
#         for bar in bars:
#             bar.set_zorder(1)
#     
#         # Create custom legend
#         eu_patch = mpatches.Patch(color='darkblue', label='Real Imports EU Countries')
#         non_eu_patch = mpatches.Patch(color='orange', label='Real Imports Non-EU Countries')
#         dot_patch = mlines.Line2D([], [], color='red', marker='o', linestyle='None', markersize=10, label='Nominal Imports')
#         ax.legend(handles=[eu_patch, non_eu_patch, dot_patch], fontsize=15)
# 
#         # Set the title with sector name instead of sector code
#         sector_name = reverse_lookup.get(sec, "Unknown Sector")
#         plt.tight_layout()
# #        plt.savefig(f'{save_path}real_exports_{config_name}_{sector_name}.{save_format}', format=save_format)
#         plt.show()
# 
# =============================================================================


##% test

# Get baseline gdp

# =============================================================================
# baseline_gdp=baseline.cons.loc[:,:,'NOR'] #dropping imports
# baseline_gdp=baseline_gdp.groupby(['row_country', 'row_sector']).sum()
# baseline_gdp=baseline_gdp.loc['NOR',:,:]
# baseline_gdp=baseline_gdp.sum()
# =============================================================================


baseline_gdp=baseline.cons.loc['NOR',:,'NOR'] #dropping imports
baseline_gdp=baseline_gdp.sum()



