from tkinter import *
from decimal import Decimal
from blinker import signal


class OptionsPanel (Frame):
    def __init__(self, master, model):
        Frame.__init__(self, master, bd=1, relief=SUNKEN)

        self.model = model

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.min_set_qty_label = Label(self, text='Min qty in sets:', anchor='w')
        self.min_set_qty_label.grid(row=0, column=0, sticky='we')

        self.spinner_min_set_qty = StringVar(self)
        self.spinner_min_set_qty.set(str(model.min_set_qty))

        self.min_set_qty = Spinbox(self, from_=0, to=50, width=4, textvariable=self.spinner_min_set_qty)
        self.min_set_qty.grid(row=0, column=1)

        self.spinner_min_set_qty.trace('w', self.on_min_set_qty_change)

        self.test = Button(self, text = "test", command = self.testing_method)
        self.test.grid(row=1, column=1)


    def on_color_picker_closed_fix_bug(self):
        self.min_set_qty.grid_forget()
        self.min_set_qty.grid(row=0, column=1)

    def on_min_set_qty_change(self, *args):
        val = self.spinner_min_set_qty.get()

        try:
            self.model.set_min_set_qty(int(val))
        except ValueError:
            pass


    def testing_method(self):
        signal('on_test_01').send(self)
