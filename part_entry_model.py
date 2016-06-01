class PartEntry:
    def __init__(self, part, part_color, count):
        self.part = part
        self.part_color = part_color
        self.count = count

    def hash(self):
        return self.part['number'] + " " + self.part_color['color_name']

class PartEntryModel:
    def __init__(self):
        self.part_entries = []
        self.selected_part_entry = {}

    def increase_part_entry(self, part_entry):
        assert part_entry in self.part_entries
        part_entry.count += 1

    def decrease_part_entry(self, part_entry):
        erased = False
        assert part_entry in self.part_entries
        part_entry.count -= 1

        if part_entry.count == 0:
            self.part_entries.remove(part_entry)
            erased = True

        return erased

    def add_part_entry(self, part, part_color):
        part_entry_ret = self.find_part_entry(part['number'], part_color['color_id'])

        if part_entry_ret:
            part_entry_ret.count += 1
        else:
            part_entry_ret = PartEntry(part, part_color, 1)
            self.part_entries.append(part_entry_ret)

        return part_entry_ret

    def find_part_entry(self, part_number, part_color_id):
        for part_entry in self.part_entries:
            if part_number == part_entry.part['number'] and part_color_id == part_entry.part_color['color_id']:
                return part_entry
        return None
