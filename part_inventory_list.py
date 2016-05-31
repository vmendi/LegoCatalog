from tkinter import *
from blinker import signal
import fetch_image


class PartInventoryList (Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bd=1, relief='sunken')

        self.canvas = Canvas(self)

        self.hbar = Scrollbar(self, orient=HORIZONTAL)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.hbar.config(command=self.canvas.xview)

        self.vbar = Scrollbar(self, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)

        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

        self.inner_frame = Frame(self.canvas)
        self.inner_frame.grid()
        self.inner_frame.grid_columnconfigure(1, weight=1)
        self.inner_frame.bind("<Configure>", self.on_inner_frame_configure)

        self.canvas_window = self.canvas.create_window((0, 0), anchor='nw', window=self.inner_frame,
                                                       tags="self.inner_frame")

        self.right_click_menu = Menu(self, tearoff=0)
        self.right_click_menu.add_command(label="Add", command = self.on_menu_add_click)
        self.right_click_menu.add_command(label="Remove", command = self.on_menu_remove_click)

        signal('on_create_part_entry').connect(self.on_create_part_entry)

        self.part_entry_widgets_map = {}

        self.part_model = PartListModel()

    def on_inner_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width() - 7)

    def on_right_button_click(self, event, part_entry):
        self.part_model.selected_part_entry = part_entry
        self.right_click_menu.post(event.x_root+1, event.y_root)

    def on_create_part_entry(self, sender, part, part_color):
        part_entry = self.part_model.add_part_entry(part, part_color)

        if part_entry['count'] == 1:
            self.create_part_entry(part_entry)
        else:
            self.update_part_entry(part_entry)

    def on_menu_add_click(self):
        self.part_model.increase_part_entry(self.part_model.selected_part_entry)
        self.update_part_entry(self.part_model.selected_part_entry)

    def on_menu_remove_click(self):
        erased = self.part_model.decrease_part_entry(self.part_model.selected_part_entry)

        if erased:
            self.delete_part_entry(self.part_model.selected_part_entry)
        else:
            self.update_part_entry(self.part_model.selected_part_entry)

    def create_part_entry(self, part_entry):
        assert PartListModel.part_entry_hash(part_entry) not in self.part_entry_widgets_map

        next_row_index = self.inner_frame.grid_size()[1] + 1

        part = part_entry['part']
        part_color = part_entry['part_color']

        part_entry_widgets = {
            'image': fetch_image.create_part_image_label(part, self.inner_frame, 0.5),
            'numba': Label(self.inner_frame, text=part['number']),
            'color': Label(self.inner_frame, text=part_color['color_name']),
            'count': Label(self.inner_frame, text=part_entry['count'])
        }

        part_entry_widgets['image'].grid(row=next_row_index, column=0, padx=5)
        part_entry_widgets['numba'].grid(row=next_row_index, column=1, sticky='ew', padx=5)
        part_entry_widgets['color'].grid(row=next_row_index, column=2, sticky='ew', padx=5)
        part_entry_widgets['count'].grid(row=next_row_index, column=3)

        self.part_entry_widgets_map[PartListModel.part_entry_hash(part_entry)] = part_entry_widgets

        for widget in part_entry_widgets.values():
            widget.bind("<Enter>",    lambda e, p=part: signal('on_mouse_over_part').send(self, part=p))
            widget.bind("<Button-2>", lambda e, p=part_entry: self.on_right_button_click(e, p))

    def delete_part_entry(self, part_entry):
        part_entry_widgets = self.part_entry_widgets_map[PartListModel.part_entry_hash(part_entry)]

        for widget in part_entry_widgets.values():
            widget.grid_remove()
            del widget

        del self.part_entry_widgets_map[PartListModel.part_entry_hash(part_entry)]


    def update_part_entry(self, part_entry):
        part_entry_widgets = self.part_entry_widgets_map[PartListModel.part_entry_hash(part_entry)]
        part_entry_widgets['count']['text'] = part_entry['count']


class PartListModel:
    def __init__(self):
        self.part_entries = []
        self.selected_part_entry = {}

    def increase_part_entry(self, part_entry):
        assert part_entry in self.part_entries
        part_entry['count'] += 1

    def decrease_part_entry(self, part_entry):
        erased = False
        assert part_entry in self.part_entries
        part_entry['count'] -= 1

        if part_entry['count'] == 0:
            self.part_entries.remove(part_entry)
            erased = True

        return erased

    def add_part_entry(self, part, part_color):
        part_entry = self.find_part_entry(part['number'], part_color['color_id'])

        if part_entry:
            part_entry['count'] += 1
        else:
            part_entry = dict(part=part,
                              count=1,
                              part_color=part_color)

            self.part_entries.append(part_entry)

        return part_entry

    def find_part_entry(self, part_number, part_color_id):
        for part_entry in self.part_entries:
            if part_number == part_entry['part']['number'] and part_color_id == part_entry['part_color']['color_id']:
                return part_entry
        return None

    @staticmethod
    def part_entry_hash(part_entry):
        return part_entry['part']['number'] + " " + part_entry['part_color']['color_name']