import json

import pymysql
import requests
from lxml import etree


def convert_bricklink_xml_to_json():
    convert_xml_to_json('data/BrickLink/', 'Parts')
    convert_xml_to_json('data/BrickLink/', 'Codes')
    convert_xml_to_json('data/BrickLink/', 'Colors')
    convert_xml_to_json('data/BrickLink/', 'Sets')


# Descarga el inventario de todos los sets y lo inserta en sql
def fetch_sets_inventories_and_insert_sql():
    for set_json in read_json('data/BrickLink/Sets.json'):
        set_id = set_json['ITEMID']
        year = set_json['ITEMYEAR']

        print("Processing set {} year {}".format(set_id, year))

        try:
            fetch_set_inventory_xml(set_id)
            convert_xml_to_json('data/BrickLink/Inventories/', set_id)
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


def fetch_set_inventory_xml(set_id):
    print('Requesting Set Inventory for set: {}'.format(set_id))

    url = 'https://www.bricklink.com/catalogDownload.asp?a=a'
    response = requests.post(url, data={'itemType': 'S', 'viewType': 4, 'itemTypeInv': 'S', 'itemNo': set_id,
                                        'downloadType': 'X'})  # downloadType: 'T' for csv instead of xml

    xml_file_name = 'data/BrickLink/Inventories/{}.xml'.format(set_id)
    with open(xml_file_name, 'w') as xml_file:
        xml_file.write(response.text)


def connect():
    cxn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", unix_socket=None, autocommit=True)
    cxn.select_db("lego_catalog")
    return cxn


def read_json(json_file):
    print("Reading JSON file: {}... ".format(json_file), end='')
    with open(json_file) as json_file:
        all_json = json.loads(json_file.read())
        print("found {} items.".format(len(all_json)))
    return all_json


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


def convert_xml_to_json(xml_path_only, xml_file_name_only):
    all_items = read_xml(xml_path_only + xml_file_name_only + ".xml")

    json_file = xml_path_only + xml_file_name_only + ".json"
    print("Saving {} to JSON file: {}".format(xml_file_name_only, json_file))
    with open(json_file, 'w') as json_file:
        json_file.write(json.dumps(all_items, indent=4))


if __name__ == '__main__':
    convert_bricklink_xml_to_json()
    fetch_sets_inventories_and_insert_sql()



