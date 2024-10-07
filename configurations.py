#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 18:05:51 2024

@author: dora
"""

import funcs_for_dora as f

EUcountries=['AUT', 'BEL', 'BGR', 'CYP', 'CZE', 'DEU', 
             'DNK', 'ESP', 'EST', 'FIN', 'FRA',  'GRC', 'HRV', 
             'HUN', 'IRL', 'ISL', 'ITA', 
             'LTU', 'LVA', 
             'MLT', 'NLD', 'POL', 
             'PRT', 'ROU', 'SVK', 'SVN', 'SWE']


allcountries=f.get_country_list()


#washing machines, solar panels, steel, aluminum, EVs
#'45T47' washing machines
# 26 solar panel
# 24 aluminum, ,steel
#29T30 vehicles

subsectors=['45T47', '26', '24', '29T30']


# Define different configurations
configurations = [
# =============================================================================
#     {
#         'name': 'the_first_test',
#         'tax_matrix_scenario': [
#             ('USA', slice(None), slice(None), 0.1),
#             ('USA', slice(None), 'USA', 0),
#             (slice(None), slice(None), 'NOR', 0.2),
#             (slice(None), '01T02', slice(None), 0.3),
#             ('BRA', '01T02', 'CHN', 1.1)
#         ]
#     },
# =============================================================================
     {
        'name': 'US10',
        'tax_matrix_scenario': [
            (slice(None), slice(None), 'USA', 0.1),
            ('USA', slice(None), 'USA', 0)
        ]
    },
    {
        'name': 'US1060',
        'tax_matrix_scenario': [
            (slice(None), slice(None), 'USA', 0.1),
            ('USA', slice(None), 'USA', 0),
            ('CHN', slice(None), 'USA', 0.6)
        ]
    },
    {
        'name': 'US2060',
        'tax_matrix_scenario': [
            (slice(None), slice(None), 'USA', 0.2),
            ('USA', slice(None), 'USA', 0),
            ('CHN', slice(None), 'USA', 0.6)
        ]
    },
    {
        'name': 'US1060EU0',
        'tax_matrix_scenario': [
            ( slice(None), slice(None), 'USA', 0.1),
            ('USA', slice(None), 'USA', 0),
            ('CHN', slice(None), 'USA', 0.6)
        ] + [(country, slice(None), 'USA', 0) for country in EUcountries]

    },
    {
        'name': 'US10Sectors',
        'tax_matrix_scenario': [
            (slice(None), sector, 'USA', 0.1) for sector in subsectors]
        + [('USA', slice(None), 'USA', 0)  ]  
    },

     {
         'name': 'US10Retal',
         'tax_matrix_scenario': [
             (slice(None), slice(None), 'USA', 0.1),
             ('USA', slice(None), 'USA', 0)
         ] + [('USA', slice(None), country, 0.1) for country in allcountries]
         + [(country, slice(None), country, 0) for country in allcountries]
     },

    {
        'name': 'US1060Retal',
        'tax_matrix_scenario': [
            (slice(None), slice(None), 'USA', 0.1),
            ('USA', slice(None), 'USA', 0),
            ('CHN', slice(None), 'USA', 0.6)
        ]
            + [('USA', slice(None), country, 0.1) for country in allcountries]
            + [(country, slice(None), country, 0) for country in allcountries]
            + [('USA', slice(None), 'CHN', 0.6)]
            + [('CHN', slice(None), 'CHN', 0)]

    },
    {
        'name': 'US2060Retal',
        'tax_matrix_scenario': [
            (slice(None), slice(None), 'USA', 0.2),
            ('USA', slice(None), 'USA', 0),
            ('CHN', slice(None), 'USA', 0.6)
        ]
            + [('USA', slice(None), country, 0.2) for country in allcountries]
            + [(country, slice(None), country, 0) for country in allcountries]
            + [('USA', slice(None), 'CHN', 0.6)]
            + [('CHN', slice(None), 'CHN', 0)]

    },
    {
        'name': 'US1060EU0Retal',
        'tax_matrix_scenario': [
            (slice(None), slice(None), 'USA', 0.1),
            ('USA', slice(None), 'USA', 0),
            ('CHN', slice(None), 'USA', 0.6)
        ]
            + [('USA', slice(None), country, 0.1) for country in allcountries]
            + [(country, slice(None), country, 0) for country in allcountries]
            + [(country, slice(None), 'USA', 0.0) for country in EUcountries]
    },
    
    {
        'name': 'US10SectorsRetal',
        'tax_matrix_scenario': [
            (slice(None), sector, slice(None), 0.1) for sector in subsectors]
        + [(country, slice(None), country, 0) for country in allcountries ] 
    },



#     {
#         'name': 'US100',
#         'tax_matrix_scenario': [
#             ('USA', slice(None), slice(None),1),
#             ('USA', slice(None), 'USA', 0),
#         ]
#     }
]




# =============================================================================
# # Example dictionary with multiple levels and broad sector classifications
# sector_classification = {
#     'Agriculture': {
#         'Agriculture': 'onshore',
#         'Fishing': 'onshore',
#     },
#     'Industry': {
#         'Mining, energy': 'offshore',
#         'Mining, non-energy': 'onshore',
#         'Food products': 'onshore',
#         'Textiles': 'onshore',
#         'Wood': 'onshore',
#         'Paper': 'onshore',
#         'Coke, petroleum': 'offshore',
#         'Chemicals': 'onshore',
#         'Pharmaceuticals': 'onshore',
#         'Plastics': 'onshore',
#         'Non-metallic minerals': 'onshore',
#         'Basic metals': 'onshore',
#         'Fabricated metals': 'onshore',
#         'Electronics': 'onshore',
#         'Electrical equipment': 'onshore',
#         'Machinery': 'onshore',
#         'Transport equipment': 'onshore',
#         'Manufacturing nec': 'onshore',
#     },
#     'Services': {
#         'Energy': 'onshore',
#         'Water supply': 'onshore',
#         'Construction': 'onshore',
#         'Wholesale, retail': 'onshore',
#         'Land transport': 'onshore',
#         'Water transport': 'onshore',
#         'Air transport': 'onshore',
#         'Warehousing': 'onshore',
#         'Post': 'onshore',
#         'Tourism': 'onshore',
#         'Media': 'onshore',
#         'Telecom': 'onshore',
#         'IT': 'onshore',
#         'Finance, insurance': 'onshore',
#         'Real estate': 'onshore',
#         'R&D': 'onshore',
#         'Administration': 'onshore',
#         'Public sector': 'onshore',
#         'Education': 'onshore',
#         'Health': 'onshore',
#         'Entertainment': 'onshore',
#         'Other service': 'onshore',
#     }
# }
# =============================================================================



sector_classification = {
    'Agriculture': {'SectorCode': '01T02', 'PrimarySecondary': 'Agriculture', 'OnOffshore': 'onshore'},
    'Fishing': {'SectorCode': '03', 'PrimarySecondary': 'Agriculture', 'OnOffshore': 'offshore'},
    'Mining, energy': {'SectorCode': '05T06', 'PrimarySecondary': 'Industry', 'OnOffshore': 'offshore'},
    'Mining, non-energy': {'SectorCode': '07T08', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Food products': {'SectorCode': '10T12', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Textiles': {'SectorCode': '13T15', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Wood': {'SectorCode': '16', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Paper': {'SectorCode': '17T18', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Coke, petroleum': {'SectorCode': '19', 'PrimarySecondary': 'Industry', 'OnOffshore': 'offshore'},
    'Chemicals': {'SectorCode': '20', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Pharmaceuticals': {'SectorCode': '21', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Plastics': {'SectorCode': '22', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Non-metallic minerals': {'SectorCode': '23', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Basic metals': {'SectorCode': '24', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Fabricated metals': {'SectorCode': '25', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Electronics': {'SectorCode': '26', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Electrical equipment': {'SectorCode': '27', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Machinery': {'SectorCode': '28', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Transport equipment': {'SectorCode': '29T30', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Manufacturing nec': {'SectorCode': '31T33', 'PrimarySecondary': 'Industry', 'OnOffshore': 'onshore'},
    'Energy': {'SectorCode': '35', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Water supply': {'SectorCode': '36T39', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Construction': {'SectorCode': '41T43', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Wholesale, retail': {'SectorCode': '45T47', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Land transport': {'SectorCode': '49', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Water transport': {'SectorCode': '50', 'PrimarySecondary': 'Services', 'OnOffshore': 'offshore'},
    'Air transport': {'SectorCode': '51', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Warehousing': {'SectorCode': '52', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Post': {'SectorCode': '53', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Tourism': {'SectorCode': '55T56', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Media': {'SectorCode': '58T60', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Telecom': {'SectorCode': '61', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'IT': {'SectorCode': '62T63', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Finance, insurance': {'SectorCode': '64T66', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Real estate': {'SectorCode': '68', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'R&D': {'SectorCode': '69T75', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Administration': {'SectorCode': '77T82', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Public sector': {'SectorCode': '84', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Education': {'SectorCode': '85', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Health': {'SectorCode': '86T88', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Entertainment': {'SectorCode': '90T93', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
    'Other service': {'SectorCode': '94T98', 'PrimarySecondary': 'Services', 'OnOffshore': 'onshore'},
}


# Assign colors to each primary sector
sector_colors = {
    'Agriculture': 'green',
    'Industry': 'blue',
    'Services': 'orange'
}

# Assign colors for on and offshore
sector_shore_colors = {
    'onshore': 'lightblue',
    'offshore': 'blue'
}


