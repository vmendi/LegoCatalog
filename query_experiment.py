import json

from collections import defaultdict, OrderedDict

from main import read_json
from operator import itemgetter


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


def filter_sets(the_sets):
    modern_sets = [the_set for the_set in the_sets
                   if the_set['ITEMYEAR'].isdigit() and int(the_set['ITEMYEAR']) >= 1995]

    print("Number of modern sets found: {}".format(len(modern_sets)))

    categories = read_json('data/BrickLink/Categories.json')

    def get_category_name(category_id):
        return next(category['CATEGORYNAME'] for category in categories if category['CATEGORY'] == category_id)

    return [the_set for the_set in modern_sets
            if "duplo" not in get_category_name(the_set['CATEGORY']).lower()]
