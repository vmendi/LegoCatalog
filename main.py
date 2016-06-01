from tkinter import *
from tkinter import ttk
from tkinter import font

import webbrowser

from blinker import signal
from decimal import Decimal

from color_picker import ColorPicker
from part_entry_model import PartEntryModel
from part_inventory_list import PartInventoryList
from weight_serial_reader import WeightSerialReader
from part_info_frame import PartInfoFrame
from part_images_grid import PartImagesGrid


class Application(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack(fill="both", expand=1)

        self.current_weight = Decimal('0')
        self.current_threshold = Decimal('0.02')

        self.part_entry_model = PartEntryModel()

        # Top frame
        self.top_frame = Frame(self)
        self.top_frame.grid(row=0, columnspan=3, sticky='we')

        self.test = Button(self.top_frame)
        self.test["text"] = "test"
        self.test["command"] = self.testing_method
        self.test.pack(side='left', padx=5)

        # Top level menu
        self.menu_bar = Menu(master)
        master.config(menu=self.menu_bar)

        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Open XML...", command = self.open_xml)
        self.menu_file.add_command(label="Save As XML...", command = self.save_xml)

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)

        # Left frame
        self.left_frame = Frame(self, bd=1, relief='sunken')
        self.left_frame.grid(row=1, column=0, sticky='n', padx=5, pady=10)

        self.weight_label = Label(self.left_frame, text=self.current_weight, width=6, anchor='e',
                                     font=font.Font(family="Helvetica", size=60),
                                     bg="#%02x%02x%02x" % (240, 240, 240))
        self.weight_label.grid()

        self.threshold_buttons_frame = Frame(self.left_frame)
        self.threshold_buttons_frame.grid()

        self.threshold_label = Label(self.threshold_buttons_frame, text='Threshold: ')
        self.threshold_label.pack(side='left')

        self.threshold_label = Label(self.threshold_buttons_frame, text=self.current_threshold, width=4, anchor='e',
                                        font=font.Font(family="Helvetica", size=20))
        self.threshold_label.pack(side='left')

        self.plus_threshold = Button(self.threshold_buttons_frame, text="+", command = self.on_plus_threshold_click)
        self.plus_threshold.pack(side='left')

        self.minus_threshold = Button(self.threshold_buttons_frame, text="-", command = self.on_minus_threshold_click)
        self.minus_threshold.pack(side='left')

        # Center Frame
        self.part_images_grid = PartImagesGrid(self)
        self.part_images_grid.grid(row=1, column=1, sticky='nswe')

        self.part_info = PartInfoFrame(self)
        self.part_info.grid(row=2, column=1, sticky='we', padx=5, pady=10)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Part inventory list (Right Frame)
        self.right_frame = PartInventoryList(self, self.part_entry_model)
        self.right_frame.grid(row=1, column=2, rowspan=2, sticky='nse', padx=5, pady=10)

        # Configure weight reader new thread
        self.my_weight_reader = WeightSerialReader()
        # self.my_weight_reader.start()
        self.check_new_weight_timer = self.after(10, self.check_new_weight)

        # Events
        signal('on_mouse_click_part').connect(self.on_mouse_click_part)
        signal('on_mouse_click_url').connect(self.on_mouse_click_url)

    def open_xml(self):
        print("TODO")

    def save_xml(self):
        print("TODO")

    def on_mouse_click_part(self, sender, part):
        # Get the parent widget (it has to be by name)
        parent_str = self.winfo_parent()
        parent = self.nametowidget(name=parent_str)

        color_picker = ColorPicker(parent, part)
        color_picker.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')


    def on_mouse_click_url(self, sender, part):
        webbrowser.open_new('http://alpha.bricklink.com/pages/clone/catalogitem.page?P=%s' % part['number'])


    def testing_method(self):
        self.current_weight = Decimal('0.80')
        self.weight_label["text"] = self.current_weight
        self.part_images_grid.create_grid(self.current_weight, self.current_threshold)
        self.after_cancel(self.check_new_weight_timer)

    def on_plus_threshold_click(self):
        self.current_threshold += Decimal('0.01')
        self.threshold_label['text'] = self.current_threshold
        self.part_images_grid.create_grid(self.current_weight, self.current_threshold)

    def on_minus_threshold_click(self):
        self.current_threshold -= Decimal('0.01')
        self.threshold_label['text'] = self.current_threshold
        self.part_images_grid.create_grid(self.current_weight, self.current_threshold)

    def check_new_weight(self):
        current_weight = self.my_weight_reader.get_last_weight()

        if current_weight != self.current_weight:
            self.current_weight = current_weight
            self.weight_label["text"] = self.current_weight
            self.part_images_grid.create_grid(self.current_weight, self.current_threshold)

        self.check_new_weight_timer = self.after(10, self.check_new_weight)


def center_window(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


if __name__ == '__main__':
    root = Tk()

    myapp = Application(master=root)
    myapp.master.title("Lego Sorter")
    myapp.master.minsize(width=500, height=200)

    root.geometry('{}x{}'.format(1400, 1000))

    center_window(root)

    myapp.mainloop()