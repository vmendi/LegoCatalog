from tkinter import *
from tkinter import font
from blinker import signal

class WeightPanel (Frame):
    def __init__(self, master, model):
        Frame.__init__(self, master, bd=1, relief='sunken')

        self.model = model

        self.weight_label = Label(self, text=model.current_weight, width=6, anchor='e',
                                  font=font.Font(family="Helvetica", size=60),
                                  bg="#%02x%02x%02x" % (240, 240, 240))
        self.weight_label.grid(row=0, column=0)

        self.threshold_buttons_frame = Frame(self)
        self.threshold_buttons_frame.grid(row=1, column=0, sticky='w')

        self.threshold_label = Label(self.threshold_buttons_frame, text='Threshold: ')
        self.threshold_label.pack(side='left')

        self.threshold_value = Label(self.threshold_buttons_frame, text=model.current_threshold, width=4, anchor='w',
                                     font=font.Font(family="Helvetica", size=20))
        self.threshold_value.pack(side='left')

        self.plus_threshold = Button(self.threshold_buttons_frame, text="+", command = self.on_plus_threshold_click)
        self.plus_threshold.pack(side='left')

        self.minus_threshold = Button(self.threshold_buttons_frame, text="-", command = self.on_minus_threshold_click)
        self.minus_threshold.pack(side='left')

        signal('on_new_weight').connect(self.on_new_weight)

    def on_new_weight(self, sender, weight, threshold):
        self.weight_label["text"] = weight
        self.threshold_value['text'] = threshold

    def on_plus_threshold_click(self):
        self.model.increase_threshold()

    def on_minus_threshold_click(self):
        self.model.decrease_threshold()