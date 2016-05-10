import json
from time import sleep

import codecs
import re
import requests
from lxml import html


# Lee los sets de un rango de anyos desde rebrickable y los graba a disco, incluyendo los part-out prices que obtiene
# de bricklink.
def save_rebrickable_sets_json():
    all_sets = []

    for year in range(2015, 2016):
        print('Requesting sets from Rebrickable for year ' + str(year) + '...', end='')

        result_string = search_rebrickable_api('json', 'S', year)
        result_json = json.loads(result_string)

        print('{} sets in {}'.format(len(result_json['results']), year))

        all_sets.extend(result_json['results'])

    print('{} sets in total'.format(len(all_sets)))

    with open('data/Rebrickable/all_sets_temp.json', 'w') as my_file:
        my_file.write(json.dumps(all_sets, sort_keys=True, indent=4))

    for lego_set in all_sets:
        print('Request part out price from Bricklink for set ' + lego_set['set_id'] +
              ' from year ' + lego_set['year'] + '...', end='')

        part_out_prices = get_part_out_price_from_bricklink(lego_set['set_id'])
        lego_set.update(part_out_prices)

        print('{}'.format(str(part_out_prices)))

        sleep(1)

    with open('data/Rebrickable/all_sets.json', 'w') as my_file:
        my_file.write(json.dumps(all_sets, sort_keys=True, indent=4))


def get_part_out_price_from_bricklink(set_complete_id):
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
        print('Error getting part out price for set ' + set_complete_id + ': ' + str(exc))
        return {}

    return {'part_out_avg_price': avg_price,
            'part_out_cur_price': current_price}


def save_colors():
    params = {
        'key': '1sBATG4Tfa',
        'format': 'csv'
    }

    response = requests.get('http://rebrickable.com/api/get_colors', params=params)

    with codecs.open('data/Rebrickable/colors.csv', 'w', 'utf-8') as my_file:
        my_file.write(response.text)


def search_rebrickable_api(response_format, search_type, year):
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

    return response.text