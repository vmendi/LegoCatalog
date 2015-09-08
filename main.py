__author__ = 'vmendi'

import requests
import json
import csv
import os
import codecs
import pprint
import unicodecsv
import re
from lxml import html
from time import sleep


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
    file_name = 'data/sets-' + str(year) + '.' + file_format

    result_string = search_from_api(file_format, 'S', year)

    with codecs.open(file_name, 'w', 'utf-8') as my_file:
        if file_format == 'json':
            my_file.write(json.dumps(json.loads(result_string), sort_keys=True, indent=4))
        elif file_format == 'csv':
            my_file.write(result_string)


def save_all_sets():
    all_sets = []

    for year in range(1995, 2016):
        print 'Requesting sets for year ' + str(year) + '...',

        result_string = search_from_api('json', 'S', year)
        result_json = json.loads(result_string)

        print '{} sets in {}'.format(len(result_json['results']), year)

        all_sets.extend(result_json['results'])

    print '{} sets in total'.format(len(all_sets))

    with open('data/all_sets_temp.json', 'w') as my_file:
        my_file.write(json.dumps(all_sets, sort_keys=True, indent=4))

    for lego_set in all_sets:
        print 'Request part out price for set ' + lego_set['set_id'] + ' from year ' + lego_set['year'] + '...',

        part_out_prices = get_part_out_price(lego_set['set_id'])
        lego_set.update(part_out_prices)

        print '{}'.format(str(part_out_prices))

        sleep(1)

    with open('data/all_sets.json', 'w') as my_file:
        my_file.write(json.dumps(all_sets, sort_keys=True, indent=4))


def get_part_out_price(set_complete_id):
    set_components = set_complete_id.split('-')
    set_id = set_components[0]
    set_version = set_components[1]

    url = 'http://www.bricklink.com/catalogPOV.asp?' \
          'itemType=S&itemNo={}&itemSeq={}&itemQty=1&breakType=M&itemCondition=N&incInstr=Y'.format(set_id, set_version)

    response = requests.get(url)
    tree = html.fromstring(response.text)

    # Inspect element -> Right click -> get XPath
    avg_price = tree.xpath('/html/body/center/table/tr[1]/td/table/tr[3]/td[1]/p/font[2]/b/text()')
    current_price = tree.xpath('/html/body/center/table/tr[1]/td/table/tr[3]/td[2]/p/font[2]/b/text()')

    # ['US $684'] => 684
    try:
        avg_price = re.match(r".*\$(\d*)", avg_price[0]).group(1)
        current_price = re.match(r".*\$(\d*)", current_price[0]).group(1)
    except Exception as exc:
        print 'Error getting part out price for set ' + set_complete_id + ': ' + exc.message
        return {}

    return {'part_out_avg_price': avg_price,
            'part_out_cur_price': current_price}

def save_all():
    result_string = ''

    for year in range(2015, 2016):
        result_string += search_from_api('csv', 'S', year)

    with codecs.open('data/all_sets.csv', 'w', 'utf-8') as my_file:
        my_file.write(result_string)

    csv_reader = csv.reader(result_string.splitlines())


def save_colors():
    params = {
        'key': '1sBATG4Tfa',
        'format': 'csv'
    }

    response = requests.get('http://rebrickable.com/api/get_colors', params=params)

    with codecs.open('data/colors.csv', 'w', 'utf-8') as my_file:
        my_file.write(response.text)

if __name__ == '__main__':

    save_all_sets()

    # print json.dumps(lego_sets, sort_keys=True, indent=4)



