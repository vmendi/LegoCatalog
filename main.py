import tkinter as tk
from tkinter import font
from decimal import Decimal
import webbrowser

from PIL import ImageTk
from weight_from_db import get_by_weight_from_db_with_threshold, fetch_part_image
from weight_serial_reader import WeightSerialReader


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack(fill="both")

        self.current_weight = Decimal('0')
        self.current_threshold = Decimal('0.02')

        # Top frame
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side="top", fill='x')

        self.plus_threshold = tk.Button(self.top_frame)
        self.plus_threshold["text"] = "+ threshold"
        self.plus_threshold["command"] = self.on_plus_threshold_click
        self.plus_threshold.pack(side='left')

        self.minus_threshold = tk.Button(self.top_frame)
        self.minus_threshold["text"] = "- threshold"
        self.minus_threshold["command"] = self.on_minus_threshold_click
        self.minus_threshold.pack(side='left')

        self.test = tk.Button(self.top_frame)
        self.test["text"] = "test"
        self.test["command"] = self.testing_method
        self.test.pack(side='right')

        # Left frame
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side="left", fill='y')

        self.weight_label = tk.Label(self.left_frame, text=self.current_weight, width=6, anchor='e',
                                     font=font.Font(family="Helvetica", size=60),
                                     bg="#%02x%02x%02x" % (240, 240, 240))
        self.weight_label.grid()

        self.threshold_label = tk.Label(self.left_frame, text=self.current_threshold, width=4, anchor='e',
                                        font=font.Font(family="Helvetica", size=20))
        self.threshold_label.grid()

        # Bottom frame
        self.image_widgets = []
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side="bottom", fill='x')

        # Configure weight reader new thread
        self.my_weight_reader = WeightSerialReader()
        self.my_weight_reader.start()
        self.check_new_weight_timer = self.after(100, self.check_new_weight)

    def testing_method(self):
        self.current_weight = Decimal('1.23')
        self.weight_label["text"] = self.current_weight
        self.create_image_widgets()
        self.after_cancel(self.check_new_weight_timer)

    def on_plus_threshold_click(self):
        self.current_threshold += Decimal('0.01')
        self.threshold_label['text'] = self.current_threshold
        self.create_image_widgets()

    def on_minus_threshold_click(self):
        self.current_threshold -= Decimal('0.01')
        self.threshold_label['text'] = self.current_threshold
        self.create_image_widgets()

    def check_new_weight(self):
        current_weight = self.my_weight_reader.get_last_weight()

        if current_weight != self.current_weight:
            self.current_weight = current_weight
            self.weight_label["text"] = self.current_weight

            self.create_image_widgets()

        self.check_new_weight_timer = self.after(100, self.check_new_weight)

    def destroy_image_widgets(self):
        for widget in self.image_widgets:
            widget.destroy()

        self.image_widgets = []

    def create_image_widgets(self):
        self.destroy_image_widgets()

        parts = get_by_weight_from_db_with_threshold(self.current_weight, self.current_threshold)

        for part in parts:
            new_frame = tk.Frame(self.bottom_frame)

            new_image_label = self.create_image_label(part, new_frame)
            new_image_label.pack()

            # new_weight_label = tk.Label(new_frame, text=str(part['weight'])+'g', font=font.Font(family="Helvetica", size=10))
            # new_weight_label.pack()

            # url link
            new_url_label = tk.Label(new_frame, text=part['number'], fg='blue', cursor='draft_large',
                                     font=font.Font(family="Helvetica", size=12))
            new_url_label.pack()
            url_link = 'http://alpha.bricklink.com/pages/clone/catalogitem.page?P=%s' % part['number']
            self.bind_url_label(new_url_label, url_link)

            # add to grid
            new_frame.grid(row=int(len(self.image_widgets) / 10), column=int(len(self.image_widgets) % 10))
            self.image_widgets.append(new_frame)

    @staticmethod
    def bind_url_label(the_label, the_url_link):
        the_label.bind("<Button-1>", lambda event: webbrowser.open_new(the_url_link))


    @staticmethod
    def create_image_label(part, new_frame):
        try:
            part_image = fetch_part_image(part['number'])
            image_tk = ImageTk.PhotoImage(part_image)

            new_image_label = tk.Label(new_frame, image=image_tk)
            new_image_label.image_tk = image_tk

        except Exception as exc:
            new_image_label = tk.Label(new_frame, text=part['number'])

        return new_image_label


def center_window(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


if __name__ == '__main__':
    root = tk.Tk()

    myapp = Application(master=root)
    myapp.master.title("Lego Sorter")
    myapp.master.minsize(width=500, height=200)

    root.geometry('{}x{}'.format(1125, 800))

    center_window(root)

    myapp.mainloop()
