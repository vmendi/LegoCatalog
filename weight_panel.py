from tkinter import *
from tkinter.font import Font
from blinker import signal

class WeightPanel (Frame):
    def __init__(self, master, model):
        Frame.__init__(self, master, bd=1, relief='sunken')

        self.model = model

        self.weight_label = Label(self, text=model.current_weight, width=5, anchor='e',
                                  font = Font(family="Helvetica", size=60),
                                  bg="#%02x%02x%02x" % (240, 240, 240))
        self.weight_label.grid(row=0, column=0, sticky='we')

        self.buttons_frame = Frame(self)
        self.buttons_frame.grid(row=1, column=0, sticky='we')

        self.buttons_frame.grid_columnconfigure(1, weight=1)

        font = Font(family="Helvetica", size=20)

        self.window_center_label = Label(self.buttons_frame, text='Center:')
        self.window_center_label.grid(row=0, column=0, sticky='w')
        self.window_center_value = Label(self.buttons_frame, text=model.current_window_center, width=4, anchor='w', font=font)
        self.window_center_value.grid(row=0, column=1, sticky='we')
        self.minus_window_center = Button(self.buttons_frame, text="-", command = self.on_minus_window_center_click)
        self.minus_window_center.grid(row=0, column=2)
        self.plus_window_center = Button(self.buttons_frame, text="+", command = self.on_plus_window_center_click)
        self.plus_window_center.grid(row=0, column=3)

        self.threshold_label = Label(self.buttons_frame, text='Threshold:')
        self.threshold_label.grid(row=1, column=0)
        self.threshold_value = Label(self.buttons_frame, text=model.current_threshold, width=4, anchor='w', font=font)
        self.threshold_value.grid(row=1, column=1, sticky='we')
        self.minus_threshold = Button(self.buttons_frame, text="-", command = self.on_minus_threshold_click)
        self.minus_threshold.grid(row=1, column=2)
        self.plus_threshold = Button(self.buttons_frame, text="+", command = self.on_plus_threshold_click)
        self.plus_threshold.grid(row=1, column=3)

        signal('on_new_weight').connect(self.on_new_weight)

    def on_new_weight(self, sender, weight, window_center, threshold, parts):
        self.weight_label["text"] = weight
        self.window_center_value['text'] = window_center
        self.threshold_value['text'] = threshold

    def on_plus_window_center_click(self):
        self.model.increase_window_center()

    def on_minus_window_center_click(self):
        self.model.decrease_window_center()

    def on_plus_threshold_click(self):
        self.model.increase_threshold()

    def on_minus_threshold_click(self):
        self.model.decrease_threshold()