import json
import requests
import codecs
import re
import os
from time import sleep
from lxml import html
from lxml import etree
from collections import defaultdict, OrderedDict
from operator import itemgetter

import pymysql

def connect():
    cxn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", unix_socket=None, autocommit=True)
    cxn.select_db("lego_catalog")
    return cxn


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


# Retorna un Dict con todas las parts, codes, categories, etc del catalogo de BrickLink. Usamos el mismo metodo para
# todos los XML porque son una lista simple con todos los ITEMs. Una vez convertido a Dict, el acceso es mas comodo.
def read_xml(xml_filename):
    print("Reading XML file: {}...".format(xml_filename))
    xml_tree = etree.parse(xml_filename)

    root = xml_tree.getroot()
    print("Number of items found: {}".format(len(root)))

    all_items = []

    for child in root:
        new_item = {}
        for child_fields in child:
            new_item[child_fields.tag] = child_fields.text
        all_items.append(new_item)

    return all_items


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

        part_out_prices = get_part_out_price(lego_set['set_id'])
        lego_set.update(part_out_prices)

        print('{}'.format(str(part_out_prices)))

        sleep(1)

    with open('data/Rebrickable/all_sets.json', 'w') as my_file:
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


def convert_bricklink_xml_to_json():
    convert_to_json('data/BrickLink/', 'Parts')
    convert_to_json('data/BrickLink/', 'Codes')
    convert_to_json('data/BrickLink/', 'Colors')
    convert_to_json('data/BrickLink/', 'Sets')

def convert_to_json(xml_path_only, xml_file_name_only):
    all_items = read_xml(xml_path_only + xml_file_name_only + ".xml")

    json_file = xml_path_only + xml_file_name_only + ".json"
    print("Saving {} to JSON file: {}".format(xml_file_name_only, json_file))
    with open(json_file, 'w') as json_file:
        json_file.write(json.dumps(all_items, indent=4))


# Descarga el inventario de todos los sets y lo graba conviertiendolo a JSON
def fetch_sets_inventories_and_save():
    for set_json in read_json('data/BrickLink/Sets.json'):
        set_id = set_json['ITEMID']
        year = set_json['ITEMYEAR']

        print("Processing set {} year {}".format(set_id, year))

        try:
            # fetch_set_inventory_xml_and_json(set_id)
            # fetch_set_inventory_csv(set_id)
            insert_inventory_sql(set_id)
        except Exception as exc:
            print('Error while reading/saving inventory for set: ' + set_id + ': ' + str(exc))

        # sleep(1.0)

def insert_inventory_sql(set_id):

    cxn = connect()
    cursor = cxn.cursor()

    inventory_json = read_json("data/BrickLink/Inventories/{}.json".format(set_id))

    for inventory_part in inventory_json:
        sql = "INSERT INTO inventories (set_number, part_number, color_id, qty, match_id, type, extra, counterpart) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (set_id, inventory_part['ITEMID'], inventory_part['COLOR'], inventory_part['QTY'],
                             inventory_part['MATCHID'], inventory_part['ITEMTYPE'], inventory_part['EXTRA'],
                             inventory_part['COUNTERPART']))

    cxn.close()


def fetch_set_inventory_xml_and_json(set_id):
    print('Requesting Set Inventory for set: {}'.format(set_id))

    url = 'https://www.bricklink.com/catalogDownload.asp?a=a'
    response = requests.post(url, data={'itemType': 'S', 'viewType': 4, 'itemTypeInv': 'S', 'itemNo': set_id,
                                        'downloadType': 'X'})

    xml_file_name = 'data/BrickLink/Inventories/{}.xml'.format(set_id)
    with open(xml_file_name, 'w') as xml_file:
        xml_file.write(response.text)

    convert_to_json('data/BrickLink/Inventories/', set_id)

def fetch_set_inventory_csv(set_id):
    print('Requesting Set Inventory for set: {}'.format(set_id))

    url = 'https://www.bricklink.com/catalogDownload.asp?a=a'
    response = requests.post(url, data={'itemType': 'S', 'viewType': 4, 'itemTypeInv': 'S', 'itemNo': set_id,
                                        'downloadType': 'T'})

    csv_file_name = 'data/BrickLink/Inventories/{}.csv'.format(set_id)
    with open(csv_file_name, 'w') as csv_file:
        csv_file.write(response.text)


def read_json(json_file):
    print("Reading JSON file: {}... ".format(json_file), end='')
    with open(json_file) as json_file:
        all_json = json.loads(json_file.read())
        print("found {} items.".format(len(all_json)))
    return all_json

def filter_sets(the_sets):
    modern_sets = [the_set for the_set in the_sets
                   if the_set['ITEMYEAR'].isdigit() and int(the_set['ITEMYEAR']) >= 1995]

    print("Number of modern sets found: {}".format(len(modern_sets)))

    categories = read_json('data/BrickLink/Categories.json')

    def get_category_name(category_id):
        return next(category['CATEGORYNAME'] for category in categories if category['CATEGORY'] == category_id)

    return [the_set for the_set in modern_sets
            if "duplo" not in get_category_name(the_set['CATEGORY']).lower()]


# Una query ad-hoc para ver como de costoso es generar este codigo vs tenerlo en mysql.
def count_set_pieces():
    filtered_sets = filter_sets(read_json('data/BrickLink/Sets.json'))

    inventoried_parts = defaultdict(lambda: 0)
    unknown_qty_count = 0
    non_parts_count = 0
    missing_inventory_count = 0

    for the_set in filtered_sets:
        set_id = the_set['ITEMID']
        try:
            with open('data/BrickLink/Inventories/{}.json'.format(set_id)) as set_inventory_json_file:
                set_inventory_json = json.load(set_inventory_json_file)

                for part in set_inventory_json:
                    if not part['QTY'].isdigit():
                        unknown_qty_count += 1
                    elif part['ITEMTYPE'] != 'P':
                        non_parts_count += 1
                    else:
                        qty = int(part['QTY'])
                        part_id = part['ITEMID']
                        inventoried_parts[part_id] += qty
        except FileNotFoundError as exc:
            missing_inventory_count += 1

    print("Number of part types: {}".format(len(inventoried_parts)))
    print("Number of non-parts (mini-figures...): {}, Missing inventories: {}, Unknown quantities for {} parts"
          .format(non_parts_count, missing_inventory_count, unknown_qty_count))

    inventoried_sorted_parts = OrderedDict(sorted(inventoried_parts.items(), key=itemgetter(1), reverse=True))
    parts = read_json('data/BrickLink/Parts.json')

    for key, value in inventoried_sorted_parts.items():

        if value <= 100:
            break

        part = next(part for part in parts if part['ITEMID'] == key)
        from html import unescape
        print("Part {}, Qty: {}, Name: {}".format(key, value, unescape(part['ITEMNAME'])))



if __name__ == '__main__':
    # save_rebrickable_sets_json()
    # convert_bricklink_xml_to_json()
    # fetch_sets_inventories_and_save()
    count_set_pieces()




