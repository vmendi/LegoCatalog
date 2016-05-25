import tkinter as tk


class PartInfoFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bd=1, relief='sunken')

        self.part_name = tk.Label(self, text='Part name:')
        self.part_name.grid(row=0, column=0, sticky='w')
        self.part_name = tk.Label(self, text='')
        self.part_name.grid(row=0, column=1, sticky='w')

        self.part_number = tk.Label(self, text='Part number:')
        self.part_number.grid(row=1, column=0, sticky='w')
        self.part_number = tk.Label(self, text='')
        self.part_number.grid(row=1, column=1, sticky='w')

        self.part_weight = tk.Label(self, text='Part weight:')
        self.part_weight.grid(row=2, column=0, sticky='w')
        self.part_weight = tk.Label(self, text='')
        self.part_weight.grid(row=2, column=1, sticky='w')

        self.part_qty = tk.Label(self, text='Part qty:')
        self.part_qty.grid(row=3, column=0, sticky='w')
        self.part_qty = tk.Label(self, text='')
        self.part_qty.grid(row=3, column=1, sticky='w')

        self.part_size = tk.Label(self, text='Part size:')
        self.part_size.grid(row=4, column=0, sticky='w')
        self.part_size = tk.Label(self, text='')
        self.part_size.grid(row=4, column=1, sticky='w')

        self.category_name = tk.Label(self, text='Category name:')
        self.category_name.grid(row=5, column=0, sticky='w')
        self.category_name = tk.Label(self, text='')
        self.category_name.grid(row=5, column=1, sticky='w')

        self.category_id = tk.Label(self, text='Category id:')
        self.category_id.grid(row=6, column=0, sticky='w')
        self.category_id = tk.Label(self, text='')
        self.category_id.grid(row=6, column=1, sticky='w')

    def set_current_part(self, part):
        self.part_name['text'] = part['name']
        self.part_number['text'] = part['number']
        self.part_weight['text'] = part['weight']
        self.part_qty['text'] = part['total_qty']
        self.part_size['text'] = part['dimensions']

        self.category_name['text'] = part['category_name']
        self.category_id['text'] = part['category_id']