import tkinter as tk

from PIL import ImageTk
from weight import get_by_weight_from_db_with_threshold, fetch_part_image


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()

        self.image_widgets = []

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side="top")

        self.hi_there = tk.Button(self.top_frame)
        self.hi_there["text"] = "Hello World"
        self.hi_there["command"] = self.create_image_widgets
        self.hi_there.pack(side="left")

        self.inner_frame = tk.Frame(self)
        self.inner_frame.pack(side="bottom", fill='x')

    def create_image_widgets(self):
        self.image_widgets = []

        parts = get_by_weight_from_db_with_threshold(0.32, 0.01)

        for part in parts:
            try:
                part_image = fetch_part_image(part['number'])
                image_tk = ImageTk.PhotoImage(part_image)

                new_label = tk.Label(self.inner_frame, image=image_tk)
                new_label.image_tk = image_tk

            except Exception as exc:
                new_label = tk.Label(self.inner_frame, text=part['number'])

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
    root.geometry('{}x{}'.format(1000, 800))

    center_window(root)

    myapp.mainloop()



