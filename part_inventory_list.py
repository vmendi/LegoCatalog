from tkinter import *


class PartInventoryList (Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bd=1, relief='sunken')

        self.canvas = Canvas(self)

        self.hbar = Scrollbar(self, orient=HORIZONTAL)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.hbar.config(command=self.canvas.xview)

        self.vbar=Scrollbar(self, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)

        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

        self.inner_frame = Frame(self.canvas)
        self.inner_frame.pack(expand=True, fill=BOTH)

        self.canvas_window = self.canvas.create_window((0, 0), anchor='nw', window=self.inner_frame,
                                                       tags="self.inner_frame")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))


    def add_part(self, part):
        new_label = Label(self.inner_frame, text=part['number'])
        new_label.grid()
