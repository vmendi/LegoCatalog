import tkinter as tk


class PartInventoryList (tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.v_scrollbar = tk.Scrollbar(self, orient='vertical')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')

        self.canvas = tk.Canvas(self, bd=0, yscrollcommand=self.v_scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.v_scrollbar.config(command=self.canvas.yview)
