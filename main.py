import tkinter as tk
from tkinter import font
from decimal import Decimal

from PIL import ImageTk
from weight import get_by_weight_from_db_with_threshold, fetch_part_image
from weight_reader import weight_reader


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, bg='red')
        self.pack(fill="both")

        self.current_weight = Decimal(0)
        self.current_threshold = Decimal('0.02')

        # Top frame
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side="top", fill='x')

        self.plus_threshold = tk.Button(self.top_frame)
        self.plus_threshold["text"] = "+ threshold"
        self.plus_threshold["command"] = self.on_plus_threshold_click
        self.plus_threshold.pack()

        self.minus_threshold = tk.Button(self.top_frame)
        self.minus_threshold["text"] = "- threshold"
        self.minus_threshold["command"] = self.on_minus_threshold_click
        self.minus_threshold.pack()

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
        self.my_weight_reader = weight_reader()
        self.my_weight_reader.start()

        self.after(100, self.check_new_weight)

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
            self.weight_label["text"] = current_weight
            self.current_weight = current_weight

            self.create_image_widgets()

        self.after(100, self.check_new_weight)

    def destroy_image_widgets(self):
        for widget in self.image_widgets:
            widget.destroy()

        self.image_widgets = []

    def create_image_widgets(self):
        self.destroy_image_widgets()

        parts = get_by_weight_from_db_with_threshold(self.current_weight, self.current_threshold)

        for part in parts:
            try:
                part_image = fetch_part_image(part['number'])
                image_tk = ImageTk.PhotoImage(part_image)

                new_label = tk.Label(self.bottom_frame, image=image_tk)
                new_label.image_tk = image_tk

            except Exception as exc:
                new_label = tk.Label(self.bottom_frame, text=part['number'])

            new_label.grid(row=int(len(self.image_widgets) / 10), column=int(len(self.image_widgets) % 10))

            self.image_widgets.append(new_label)


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

    root.geometry('{}x{}'.format(1100, 800))

    center_window(root)

    myapp.mainloop()