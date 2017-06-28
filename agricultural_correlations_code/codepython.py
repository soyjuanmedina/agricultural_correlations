# Necesary imports
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from collections import OrderedDict
import urllib.request as urllib2
from pyjstat import pyjstat
import textwrap as tw

# Ask for the first filter
print('Chose a type of data you want to consult')
x = 0
for root, dirs, files in os.walk("./databases", topdown=False):
    for name in dirs:
        x = x + 1
        print(x, name)

sel = input('Input your selection: ')
folder = dirs[int(sel) - 1]
path = './databases/' + folder + '/'

# Creating the dict to storage all databases
databases = dict()

# Create the variables to the x axis
first_year = 5000
last_year = 0

# Creating the data for each database
for y in range(1, 3):

    # Creating the dict to storage each database
    databases[y] = dict()

    # Asked for the data to show
    x = 0
    printed_databases = []
    print('Select the two databases contains data you want compare')
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            printed_databases.insert(len(printed_databases), name)
            x += 1
            data_file = path+name
            data = pd.read_json(data_file, orient='columns')
            print(x, data['dataset']['label'])

    # Storage the data for each database
    databases[y]['number'] = eval(input('Select the database ' + str(y) + ': '))
    databases[y]['name'] = files[int(databases[y]['number']) - 1]
    databases[y]['name_to_url'] = files[int(databases[y]['number']) - 1].split('.')[0]
    databases[y]['path'] = path+databases[y]['name']
    databases[y]['data'] = pd.read_json(databases[y]['path'], orient='columns')
    databases[y]['years'] = (
        list(databases[y]['data']['dataset']['dimension']['Year']['category']['label'].values())
    )
    databases[y]['index'] = (
        list(databases[y]['data']['dataset']['dimension']['Statistic']['category']['index'].keys())[0]
    )
    databases[y]['unit'] = (
        databases[y]['data']['dataset']['dimension']['Statistic']['category']['unit'][databases[y]['index']]['base']
    )

    # Compare the year for the x axis
    first_year_database = int(databases[y]['years'][0])
    last_year_database = int(databases[y]['years'][-1])
    if first_year_database < first_year:
        first_year = first_year_database
    if last_year_database > last_year:
        last_year = last_year_database

y = 1
for database in databases:
    dimension2 = list(databases[y]['data']['dataset']['dimension'].keys())[0]
    question = 'Chose the ' + dimension2 + ' for your ' + str(y) + ' database'
    print(question)

    # Print options
    options = (
        list(databases[y]['data']['dataset']['dimension'][dimension2]['category']['label'].values())
    )
    x = 0
    for option in options:
        x = x + 1
        print(x, option)

    # Capturing the option
    databases[y]['option'] = eval(input('Chose the ' + dimension2 + ': '))

    # Capturing the option name
    databases[y]['option_name'] = (
        list(databases[y]['data']['dataset']['dimension'][dimension2]['category']['label'].values())[databases[y]['option']-1]
    )

    # Obtain the url to read the dataset from CSO
    databases[y]['url'] = (
        'http://www.cso.ie/StatbankServices/StatbankServices.svc/jsonservice/responseinstance/'+ databases[y]['name_to_url']
    )

    # Read the dataset
    jsonurl_data = json.load(urllib2.urlopen(databases[y]['url']), object_pairs_hook=OrderedDict)
    jsonurl_ddbb = pyjstat.from_json_stat(jsonurl_data)

    # Get the first result, since we're using only one input dataset
    jsonurl_dataset = jsonurl_ddbb[0]

    # Filter the dataset to the selected option
    databases[y]['dataset_filter_data'] = (
        jsonurl_dataset[jsonurl_dataset[dimension2] == databases[y]['option_name']]
    )

    y += 1

# Obtain data to first axis y
values1 = databases[1]['dataset_filter_data']['value']
min_axis_y1 = values1.min() * 0.95
max_axis_y1 = values1.max() * 1.05

# Obtain data to second axis y
values2 = databases[2]['dataset_filter_data']['value']
min_axis_y2 = values2.min() * 0.95
max_axis_y2 = values2.max() * 1.05

# Start the sesion for matplotlib
plt.ion()

# Create the x axis
plt.xlabel('Years')
plt.xlim(first_year, last_year)

# Create the first y axis
plt.ylabel(databases[1]['unit'])
plt.ylim(min_axis_y1, max_axis_y1)
plt.plot(
    databases[1]['years'], values1, color="blue", linewidth=2.5, linestyle="-", label=databases[1]['option_name']
)
plt.legend(loc='upper left', frameon=True)

# Create the second y axis
plt.twinx()
plt.ylabel(databases[2]['unit'])
plt.ylim(min_axis_y2, max_axis_y2)
plt.plot(
    databases[2]['years'], values2, color="red",  linewidth=2.5, linestyle="-", label=databases[2]['option_name']
)
plt.legend(loc='upper right', frameon=True)

comment2_txt = (
    databases[1]['data']['dataset']['label'] + " (blue)" + ' compare to ' + databases[2]['data']['dataset']['label'] + " (red)"
)
fig_txt = tw.fill(tw.dedent(comment2_txt.rstrip()), width=80)

# The YAxis value is -0.07 to push the text down slightly
plt.figtext(0.5, -0.2, fig_txt, horizontalalignment='center',
            fontsize=12, multialignment='left',
            bbox=dict(boxstyle="round", facecolor='#D8D8D8',
                      ec="0.5", pad=0.5, alpha=1), fontweight='bold')
