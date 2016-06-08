from tkinter import *
from tkinter.font import Font
from blinker import signal
from color_picker import ColorPicker
import fetch_image


class PartInventoryList (Frame):
    def __init__(self, master, part_entry_list):
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
        self.inner_frame.grid_columnconfigure(3, weight=1)
        self.inner_frame.bind("<Configure>", self.on_inner_frame_configure)

        self.canvas_window = self.canvas.create_window((0, 0), anchor='nw', window=self.inner_frame,
                                                       tags="self.inner_frame")

        self.right_click_menu = Menu(self, tearoff=0)
        self.right_click_menu.add_command(label="Add", command = self.on_menu_add_click)
        self.right_click_menu.add_command(label="Remove", command = self.on_menu_remove_click)

        self.part_entry_widgets_map = {}
        self.part_entry_list = part_entry_list

        self.small_font = Font(size=10)


    def on_inner_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width() - 7)

    def on_right_button_click(self, event, part_entry):
        self.part_entry_list.selected_part_entry = part_entry
        self.right_click_menu.post(event.x_root+1, event.y_root)

    def add_part_entry(self, part_entry):
        if part_entry.count == 1:
            self.create_part_entry(part_entry)
        else:
            self.update_part_entry(part_entry)

    def on_menu_add_click(self):
        self.part_entry_list.increase_part_entry(self.part_entry_list.selected_part_entry)
        self.update_part_entry(self.part_entry_list.selected_part_entry)

    def on_menu_remove_click(self):
        erased = self.part_entry_list.decrease_part_entry(self.part_entry_list.selected_part_entry)

        if erased:
            self.delete_part_entry(self.part_entry_list.selected_part_entry)
        else:
            self.update_part_entry(self.part_entry_list.selected_part_entry)

    def create_part_entry(self, part_entry):
        assert part_entry.hash() not in self.part_entry_widgets_map

        next_row_index = self.inner_frame.grid_size()[1] + 1

        part = part_entry.part
        part_color = part_entry.part_color

        part_entry_widgets = {
            'image': fetch_image.create_part_image_label(part, self.inner_frame, 0.5),
            'numba': Label(self.inner_frame, text=part['number'], font=self.small_font),
            'color': Label(self.inner_frame, text=part_color['color_name'], font=self.small_font, anchor='w'),
            'count': Label(self.inner_frame, text=part_entry.count),
            'order': Label(self.inner_frame, text=part['ordering']),
            'color_image': ColorPicker.create_part_color_label(self.inner_frame, (16, 32), part_color['rgb'])
        }

        part_entry_widgets['image'].grid(row=next_row_index, column=0, padx=3)
        part_entry_widgets['color_image'].grid(row=next_row_index, column=1, sticky='w')
        part_entry_widgets['numba'].grid(row=next_row_index, column=2, sticky='w')
        part_entry_widgets['color'].grid(row=next_row_index, column=3, sticky='w')
        part_entry_widgets['order'].grid(row=next_row_index, column=4, sticky='e')
        part_entry_widgets['count'].grid(row=next_row_index, column=5)

        self.part_entry_widgets_map[part_entry.hash()] = part_entry_widgets

        for widget in part_entry_widgets.values():
            widget.bind("<Enter>",    lambda e, p=part: signal('on_mouse_over_part').send(self, part=p))
            widget.bind("<Button-2>", lambda e, p=part_entry: self.on_right_button_click(e, p))

    def delete_part_entry(self, part_entry):
        part_entry_widgets = self.part_entry_widgets_map[part_entry.hash()]

        for widget in part_entry_widgets.values():
            widget.grid_remove()
            del widget

        del self.part_entry_widgets_map[part_entry.hash()]


    def update_part_entry(self, part_entry):
        part_entry_widgets = self.part_entry_widgets_map[part_entry.hash()]
        part_entry_widgets['count']['text'] = part_entry.count
