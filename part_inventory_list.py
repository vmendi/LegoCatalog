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

        signal('on_mouse_click_part').connect(self.on_mouse_click_part)

        self.part_model = PartListModel()


    def on_inner_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width() - 7)


    def on_mouse_click_part(self, sender, part):
        part_entry = self.part_model.add_part_entry(part, None)

        if part_entry['count'] == 1:
            self.create_part_entry(part_entry)
        else:
            self.update_part_entry(part_entry)

    def on_button_plus_click(self, part_entry):
        self.part_model.increase_part_entry(part_entry)
        self.update_part_entry(part_entry)

    def on_button_minus_click(self, part_entry):
        erased = self.part_model.decrease_part_entry(part_entry)

        if erased:
            self.delete_part_entry(part_entry)
        else:
            self.update_part_entry(part_entry)

    def create_part_entry(self, part_entry):
        grid_size = self.inner_frame.grid_size()

        next_row_index = grid_size[1] + 1

        part = part_entry['part']
        part_count = part_entry['count']

        new_image = fetch_image.create_image_label(part, self.inner_frame, 0.5)
        new_number = Label(self.inner_frame, text=part['number'])
        new_count = Label(self.inner_frame, text=part_count)

        new_image.grid(row=next_row_index, column=0, padx=5)
        new_number.grid(row=next_row_index, column=1, sticky='w', padx=5)
        new_count.grid(row=next_row_index, column=2)

        new_image.bind ("<Enter>", lambda e, p=part: signal('on_mouse_over_part').send(self, part=p))
        new_number.bind("<Enter>", lambda e, p=part: signal('on_mouse_over_part').send(self, part=p))
        new_count.bind ("<Enter>", lambda e, p=part: signal('on_mouse_over_part').send(self, part=p))

        button_plus  = Button(self.inner_frame, text="+", command=lambda p=part_entry: self.on_button_plus_click(p))
        button_minus = Button(self.inner_frame, text="-", command=lambda p=part_entry: self.on_button_minus_click(p))

        button_plus.grid(row=next_row_index, column=3, sticky='e')
        button_minus.grid(row=next_row_index, column=4, sticky='e')

    def delete_part_entry(self, part_entry):
        row_entry = self.find_row_entry(part_entry)
        for widget in row_entry:
            widget.grid_remove()
            del widget

    def update_part_entry(self, part_entry):
        row_entry = self.find_row_entry(part_entry)
        row_entry[2]['text'] = part_entry['count']

    def find_row_entry(self, part_entry):
        grid_size = self.inner_frame.grid_size()

        for row_index in range(grid_size[1]):
            row_entry = self.inner_frame.grid_slaves(row_index)
            if len(row_entry) > 0 and row_entry[3]['text'] == part_entry['part']['number']:
                return row_entry


class PartListModel:
    def __init__(self):
        self.part_entries = []

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

    def add_part_entry(self, part, color):
        part_entry = self.find_part_entry(part)

        if part_entry:
            part_entry['count'] += 1
        else:
            part_entry = dict(part=part,
                              count=1,
                              color="blah")

            self.part_entries.append(part_entry)

        return part_entry

    def find_part_entry(self, part):
        for part_entry in self.part_entries:
            if part['number'] == part_entry['part']['number']:
                return part_entry
        return None

    def contains_part(self, part):
        for part_entry in self.part_entries:
            if part['number'] == part_entry['part']['number']:
                return True
        return False