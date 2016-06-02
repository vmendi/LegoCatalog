from tkinter import *
from tkinter.filedialog import asksaveasfilename
import webbrowser
from decimal import Decimal
import db

from options_panel import OptionsPanel
from blinker import signal
from color_picker import ColorPicker
from part_inventory_list import PartInventoryList
from part_info_frame import PartInfoFrame
from part_images_grid import PartImagesGrid
from weight_panel import WeightPanel
from model import Model


class Application(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.master = master
        self.place(relwidth=1, relheight=1)

        self.model = Model()

        # Top level menu
        self.menu_bar = Menu(master)
        master.config(menu=self.menu_bar)

        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Save As XML...", command = self.save_xml)

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)

        # Weight Panel (Left frame)
        self.weight_panel = WeightPanel(self, self.model)
        self.weight_panel.grid(row=0, column=0, sticky='n', padx=5, pady=10)

        # Options Panel
        self.options_panel = OptionsPanel(self, self.model)
        self.options_panel.grid(row=1, column=0, sticky='wes', padx=5, pady=10)

        # Center Frame
        self.part_images_grid = PartImagesGrid(self)
        self.part_images_grid.grid(row=0, column=1, sticky='nswe', pady=10)

        self.part_info = PartInfoFrame(self)
        self.part_info.grid(row=1, column=1, sticky='we', padx=5, pady=10)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Part inventory list (Right Frame)
        self.right_frame = PartInventoryList(self, self.model.part_entry_list)
        self.right_frame.grid(row=0, column=2, rowspan=2, sticky='nse', padx=5, pady=10)

        # Events
        signal('on_mouse_click_part').connect(self.on_mouse_click_part)
        signal('on_mouse_click_url').connect(self.on_mouse_click_url)
        signal('on_new_weight').connect(self.on_new_weight)
        signal('on_create_part_entry').connect(self.on_create_part_entry)
        signal('on_mouse_over_part').connect(self.on_mouse_over_part)
        signal('on_test_01').connect(self.on_test_01)

        self.check_new_weight_timer = self.after(10, self.check_new_weight)


    def on_test_01(self, sender):
        self.after_cancel(self.check_new_weight_timer)
        self.model.set_current_weight(weight=Decimal('0.80'), threshold=Decimal('0.02'))


    def check_new_weight(self):
        self.model.check_new_weight()
        self.check_new_weight_timer = self.after(10, self.check_new_weight)


    def save_xml(self):
        name = asksaveasfilename(initialdir="data/",
                                 initialfile="default.xml",
                                 defaultextension='xml',
                                 title = "Choose a file name to save")
        if name:
            self.model.part_entry_list.save_xml(name)


    def on_create_part_entry(self, sender, part, part_color):
        self.right_frame.add_part_entry(part, part_color)
        self.options_panel.after_on_create_part_entry_bug()


    def on_new_weight(self, sender, weight, threshold):
        parts = db.get_by_weight_from_db_with_threshold(self.model.current_weight,
                                                        self.model.current_threshold,
                                                        self.model.min_set_qty)
        self.part_images_grid.create_grid(parts)


    def on_mouse_click_part(self, sender, part):
        color_picker = ColorPicker(self.master, part)
        color_picker.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')


    def on_mouse_over_part(self, sender, part):
        self.part_info.set_current_part(part)


    def on_mouse_click_url(self, sender, part):
        webbrowser.open_new('http://alpha.bricklink.com/pages/clone/catalogitem.page?P=%s' % part['number'])


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