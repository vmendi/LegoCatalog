from tkinter import *
from tkinter import font
from decimal import Decimal
from blinker import signal

from weight_serial_reader import WeightSerialReader


class WeightPanel (Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bd=1, relief='sunken')

        self.current_weight = Decimal('0.0')
        self.current_threshold = Decimal('0.02')

        self.weight_label = Label(self, text=self.current_weight, width=6, anchor='e',
                                  font=font.Font(family="Helvetica", size=60),
                                  bg="#%02x%02x%02x" % (240, 240, 240))
        self.weight_label.grid()

        self.threshold_buttons_frame = Frame(self)
        self.threshold_buttons_frame.grid()

        self.threshold_label = Label(self.threshold_buttons_frame, text='Threshold: ')
        self.threshold_label.pack(side='left')

        self.threshold_value = Label(self.threshold_buttons_frame, text=self.current_threshold, width=4, anchor='w',
                                     font=font.Font(family="Helvetica", size=20))
        self.threshold_value.pack(side='left')

        self.plus_threshold = Button(self.threshold_buttons_frame, text="+", command = self.on_plus_threshold_click)
        self.plus_threshold.pack(side='left')

        self.minus_threshold = Button(self.threshold_buttons_frame, text="-", command = self.on_minus_threshold_click)
        self.minus_threshold.pack(side='left')

        if sys.gettrace():
            self.test = Button(self, text = "test", command = self.testing_method)
            self.test.grid()

        # Configure weight reader new thread
        self.my_weight_reader = WeightSerialReader()
        # self.my_weight_reader.start()
        self.check_new_weight_timer = self.after(10, self.check_new_weight)

    def on_plus_threshold_click(self):
        self.current_threshold += Decimal('0.01')
        self.threshold_value['text'] = self.current_threshold
        signal('on_new_weight').send(self, weight=self.current_weight, threshold=self.current_threshold)

    def on_minus_threshold_click(self):
        self.current_threshold -= Decimal('0.01')
        self.threshold_value['text'] = self.current_threshold
        signal('on_new_weight').send(self, weight=self.current_weight, threshold=self.current_threshold)

    def check_new_weight(self):
        current_weight = self.my_weight_reader.get_last_weight()

        if current_weight != self.current_weight:
            self.current_weight = current_weight
            self.weight_label["text"] = self.current_weight
            signal('on_new_weight').send(self, weight=self.current_weight, threshold=self.current_threshold)

        self.check_new_weight_timer = self.after(10, self.check_new_weight)


    def testing_method(self):
        self.current_weight = Decimal('0.80')
        self.weight_label["text"] = self.current_weight
        signal('on_new_weight').send(self, weight=self.current_weight, threshold=self.current_threshold)
        self.after_cancel(self.check_new_weight_timer)