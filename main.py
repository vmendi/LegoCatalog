__author__ = 'vmendi'

import requests
import json
import csv
import os
import codecs
import pprint
import unicodecsv


def search_from_api(response_format, search_type, year):
    params = {
        'key': '1sBATG4Tfa',
        'format': response_format,
        'type': search_type,
        'query': '',
        'theme1': '',
        'theme2': '',
        'theme3': '',
        'min_pieces': '',
        'max_pieces': '',
        'min_year': year,
        'max_year': year,
        'part_type_id': '',
        'part_color': '',
        'setheader': 0
    }
    response = requests.get('http://rebrickable.com/api/search', params=params)

    # csvreader = csv.reader(response.text.splitlines())
    # for row in csvreader:
    #     print row[0]

    return response.text

def save_sets(file_format, year):
    file_name = 'data/sets' + str(year) + '.' + file_format

    result_string = search_from_api(file_format, 'S', year)

    with codecs.open(file_name, 'w', 'utf-8') as my_file:
        if file_format == 'json':
            my_file.write(json.dumps(json.loads(result_string), sort_keys=True, indent=4))
        elif file_format == 'csv':
            my_file.write(result_string)

def save_all_sets():
    save_sets('json', 2015)
    save_sets('csv', 2015)


def save_all():
    result_string = ''

    for year in range(2014, 2016):
        result_string += search_from_api('csv', 'S', year)

    with codecs.open('data/all_sets.csv', 'w', 'utf-8') as my_file:
        my_file.write(result_string)

def save_colors():
    params = {
        'key': '1sBATG4Tfa',
        'format': 'csv'
    }

    response = requests.get('http://rebrickable.com/api/get_colors', params=params)

    with codecs.open('data/colors.csv', 'w', 'utf-8') as my_file:
        my_file.write(response.text)

if __name__ == '__main__':

    save_all()


    # print json.dumps(lego_sets, sort_keys=True, indent=4)



