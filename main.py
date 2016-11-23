from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import askokcancel
import webbrowser
import db
from decimal import Decimal

from options_panel import OptionsPanel
from blinker import signal
from color_picker import ColorPicker
from part_inventory_list import PartInventoryList
from part_info_frame import PartInfoFrame
from part_images_grid import PartImagesGrid
from weight_panel import WeightPanel
from part_weighings_panel import PartWeighingsPanel
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

        # Left frame, which contains WeightPanel, part_number_filter and PartWeighingsPanel
        self.left_frame = Frame(self)
        self.left_frame.grid(row=0, column=0, sticky='ns')

        # Weight Panel (Inside left frame)
        self.weight_panel = WeightPanel(self.left_frame, self.model)
        self.weight_panel.grid(row=0, column=0, sticky='n', padx=5, pady=5)

        # Part number filer (Inside left frame)
        self.part_number_filter_txt = StringVar(self)
        self.part_number_filter_txt.trace('w', self.on_part_number_filter_txt_change)

        self.part_number_filter = Entry(self.left_frame, textvariable=self.part_number_filter_txt)
        self.part_number_filter.grid(row=1, column=0, sticky='we', padx=5)

        # Weighing clusters (Inside left frame too)
        self.weighings_panel = PartWeighingsPanel(self.left_frame)
        self.weighings_panel.grid(row=2, column=0, sticky='nwe', padx=5, pady=5)

        # Options Panel
        self.options_panel = OptionsPanel(self, self.model)
        self.options_panel.grid(row=3, column=0, sticky='s', padx=5, pady=10)

        # Center Frame
        self.part_images_grid = PartImagesGrid(self)
        self.part_images_grid.grid(row=0, rowspan=3, column=1, sticky='nswe', pady=10)

        self.part_info = PartInfoFrame(self)
        self.part_info.grid(row=3, column=1, sticky='we', padx=5, pady=10)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, minsize=360)
        self.grid_rowconfigure(0, weight=1)

        # Part inventory list (Right Frame)
        self.right_frame = PartInventoryList(self, self.model.part_entry_list)
        self.right_frame.grid(row=0, column=2, rowspan=2, sticky='nsew', padx=5, pady=10)

        # Events
        signal('on_mouse_click_part').connect(self.on_mouse_click_part)
        signal('on_mouse_click_url').connect(self.on_mouse_click_url)
        signal('on_color_picker_closed').connect(self.on_color_picker_closed)
        signal('on_test_01').connect(self.on_test_01)

        self.check_new_weight_timer = self.after(30, self.check_new_weight)


    def on_test_01(self, sender):
        self.after_cancel(self.check_new_weight_timer)
        self.model.set_current_weight(weight=Decimal('0.90'), threshold=Decimal('0.12'))

    def on_part_number_filter_txt_change(self, *args):
        val = self.part_number_filter_txt.get()
        self.model.set_part_number_filter(val)

        if len(val) == 0:
            self.part_number_filter.config(bg='white')
        elif len(val) < 4:
            self.part_number_filter.config(bg='red')
        else:
            self.part_number_filter.config(bg='white')

    def check_new_weight(self):
        self.model.check_new_weight()
        self.check_new_weight_timer = self.after(30, self.check_new_weight)


    def save_xml(self):
        name = asksaveasfilename(initialdir="data/",
                                 initialfile="default.xml",
                                 defaultextension='xml',
                                 title = "Choose a file name to save")
        if name:
            self.model.part_entry_list.save_xml(name)


    def on_color_picker_closed(self, sender, part, part_color):

        # Was cancel?
        if part is not None and part_color is not None:
            # Ask for confirmation in case of creating a new mold
            actually_insert = True
            if not db.get_closest_cluster(part['number'], self.model.current_weight):
                if not askokcancel("New Mold!", "A new mold will be created. Are you sure?"):
                    actually_insert = False

            if actually_insert:
                # Create the part in the model
                part_entry = self.model.on_new_weighing(part, part_color)

                # Add it to the UI
                self.right_frame.add_part_entry(part_entry)

        self.options_panel.on_color_picker_closed_fix_bug()
        self.model.refresh_parts()


    def on_mouse_click_part(self, sender, part):
        color_picker = ColorPicker(self.master, part)
        color_picker.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')

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

    root.geometry('{}x{}'.format(1440, 1000))

    center_window(root)

    def on_mouse_wheel(event):
        signal('on_mouse_global_wheel').send(root, mouse_event=event)

    root.bind("<MouseWheel>", on_mouse_wheel)

    def on_closing():
        root.destroy()
        myapp.model.my_weight_reader.stop()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    while True:
        try:
            myapp.mainloop()
            break
        except UnicodeDecodeError:
            pass