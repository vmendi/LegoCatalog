from tkinter import *
from tkinter.filedialog import asksaveasfilename

from blinker import signal
import webbrowser

from color_picker import ColorPicker
from part_entry_model import PartEntryModel
from part_inventory_list import PartInventoryList
from part_info_frame import PartInfoFrame
from part_images_grid import PartImagesGrid
from weight_panel import WeightPanel


class Application(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack(fill="both", expand=1)

        self.part_entry_model = PartEntryModel()

        # Top level menu
        self.menu_bar = Menu(master)
        master.config(menu=self.menu_bar)

        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Save As XML...", command = self.save_xml)

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)

        # Left frame
        self.left_frame = WeightPanel(self)
        self.left_frame.grid(row=0, column=0, sticky='n', padx=5, pady=10)

        # Center Frame
        self.part_images_grid = PartImagesGrid(self)
        self.part_images_grid.grid(row=0, column=1, sticky='nswe', pady=10)

        self.part_info = PartInfoFrame(self)
        self.part_info.grid(row=1, column=1, sticky='we', padx=5, pady=10)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Part inventory list (Right Frame)
        self.right_frame = PartInventoryList(self, self.part_entry_model)
        self.right_frame.grid(row=0, column=2, rowspan=2, sticky='nse', padx=5, pady=10)

        # Events
        signal('on_mouse_click_part').connect(self.on_mouse_click_part)
        signal('on_mouse_click_url').connect(self.on_mouse_click_url)
        signal('on_new_weight').connect(self.on_new_weight)
        signal('on_create_part_entry').connect(self.on_create_part_entry)
        signal('on_mouse_over_part').connect(self.on_mouse_over_part)

    def save_xml(self):
        name = asksaveasfilename(initialdir="data/",
                                 initialfile="default.xml",
                                 defaultextension='xml',
                                 title = "Choose a file name to save")
        if name:
            self.part_entry_model.save_xml(name)


    def on_create_part_entry(self, sender, part, part_color):
        self.right_frame.add_part_entry(part, part_color)

    def on_new_weight(self, sender, weight, threshold):
        self.part_images_grid.create_grid(weight, threshold)

    def on_mouse_click_part(self, sender, part):
        # Get the parent widget (it has to be by name)
        parent_str = self.winfo_parent()
        parent = self.nametowidget(name=parent_str)

        color_picker = ColorPicker(parent, part)
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