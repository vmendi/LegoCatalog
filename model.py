from decimal import Decimal
from blinker import signal
from lxml import etree
from weight_serial_reader import WeightSerialReader


class Model:
    def __init__(self):
        self.part_entry_list = PartEntryList()

        self.current_weight = Decimal('0.0')
        self.current_threshold = Decimal('0.02')

        # Configure weight reader new thread
        self.my_weight_reader = WeightSerialReader()
        self.my_weight_reader.start()

    def increase_threshold(self):
        self.current_threshold += Decimal('0.01')
        signal('on_new_weight').send(self, weight=self.current_weight, threshold=self.current_threshold)

    def decrease_threshold(self):
        self.current_threshold -= Decimal('0.01')
        signal('on_new_weight').send(self, weight=self.current_weight, threshold=self.current_threshold)

    def set_current_weight(self, weight, threshold):
        self.current_weight = weight
        self.current_threshold = threshold
        signal('on_new_weight').send(self, weight=self.current_weight, threshold=self.current_threshold)

    def check_new_weight(self):
        next_weight = self.my_weight_reader.get_last_weight()

        if next_weight != self.current_weight:
            self.current_weight = next_weight
            signal('on_new_weight').send(self, weight=self.current_weight, threshold=self.current_threshold)

class PartEntry:
    def __init__(self, part, part_color, count):
        self.part = part
        self.part_color = part_color
        self.count = count

    def hash(self):
        return self.part['number'] + " " + self.part_color['color_name']


class PartEntryList:
    def __init__(self):
        self.part_entries = []
        self.selected_part_entry = {}

    def increase_part_entry(self, part_entry):
        assert part_entry in self.part_entries
        part_entry.count += 1

        self.save_xml('data/_backup.xml')

    def decrease_part_entry(self, part_entry):
        erased = False
        assert part_entry in self.part_entries
        part_entry.count -= 1

        if part_entry.count == 0:
            self.part_entries.remove(part_entry)
            erased = True

        self.save_xml('data/_backup.xml')

        return erased

    def add_part_entry(self, part, part_color):
        part_entry_ret = self.find_part_entry(part['number'], part_color['color_id'])

        if part_entry_ret:
            part_entry_ret.count += 1
        else:
            part_entry_ret = PartEntry(part, part_color, 1)
            self.part_entries.append(part_entry_ret)

        self.save_xml('data/_backup.xml')

        return part_entry_ret

    def find_part_entry(self, part_number, part_color_id):
        for part_entry in self.part_entries:
            if part_number == part_entry.part['number'] and part_color_id == part_entry.part_color['color_id']:
                return part_entry
        return None

    def save_xml(self, file_name):
        inventory = etree.Element('INVENTORY')

        for part_entry in self.part_entries:

            item = etree.SubElement(inventory, 'ITEM')

            item_id = etree.SubElement(item, 'ITEMID')
            item_id.text = part_entry.part['number']

            color = etree.SubElement(item, 'COLOR')
            color.text = str(part_entry.part_color['color_id'])

            category = etree.SubElement(item, 'CATEGORY')
            category.text = str(part_entry.part['category_id'])

            qty = etree.SubElement(item, 'QTY')
            qty.text = str(part_entry.count)

            item_type = etree.SubElement(item, 'ITEMTYPE')
            item_type.text = 'P'

            condition = etree.SubElement(item, 'CONDITION')
            condition.text = 'U'

        et = etree.ElementTree(inventory)
        et.write(file_name, pretty_print=True)
