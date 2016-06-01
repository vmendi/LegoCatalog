from tkinter import *
from decimal import Decimal
from blinker import signal


class OptionsPanel (Frame):
    def __init__(self, master, model):
        Frame.__init__(self, master, bd = 1, relief = SUNKEN)

        self.model = model

        self.min_qty_label = Label(self, text='Min sets:')
        self.min_qty_label.grid(row=0, column=0)

        self.spinner_value = StringVar(self)
        self.spinner_value.set("1")

        self.min_qty = Spinbox(self, from_=0, to=10, width=5, textvariable=self.spinner_value)
        self.min_qty.grid(row=0, column=1)

        self.spinner_value.trace('w', self.on_min_qty_change)

        self.test = Button(self, text = "test", command = self.testing_method)
        self.test.grid(row=1, column=1)


    def on_min_qty_change(self, *args):
        val = self.spinner_value.get()


    def testing_method(self):
        signal('on_test_01').send(self)
