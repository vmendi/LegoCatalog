from tkinter import *
from tkinter import font
from blinker import signal
import db
import fetch_image


class PartImagesGrid (Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bd = 1, relief = SUNKEN)

        self.image_widgets = []

        self.canvas = Canvas(self)

        self.vbar = Scrollbar(self, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)

        self.canvas.config(yscrollcommand=self.vbar.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

        self.inner_frame = Frame(self.canvas)
        self.inner_frame.grid()
        self.inner_frame.bind("<Configure>", self.on_inner_frame_configure)

        self.canvas_window = self.canvas.create_window((0, 0), anchor='nw', window=self.inner_frame,
                                                       tags="self.inner_frame")

    def on_inner_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width() - 7)

    def destroy_grid(self):
        for widget in self.image_widgets:
            widget.destroy()

        self.image_widgets = []

    def create_grid(self, current_weight, current_threshold):
        self.destroy_grid()

        parts = db.get_by_weight_from_db_with_threshold(current_weight, current_threshold)

        for part in parts:
            new_frame = Frame(self.inner_frame)

            # Image
            new_image_label = fetch_image.create_part_image_label(part, new_frame)
            new_image_label.pack()

            # URL link
            new_url_label = Label(new_frame, text=part['number'], fg='blue', cursor='draft_large',
                                     font=font.Font(family="Helvetica", size=12))
            new_url_label.pack()

            # Add to grid
            new_frame.grid(row=int(len(self.image_widgets) / 10), column=int(len(self.image_widgets) % 10))
            self.image_widgets.append(new_frame)

            # Emit events
            new_url_label.bind("<Button-1>", lambda e, p=part: signal('on_mouse_click_url').send(self, part=p))
            new_frame.bind("<Enter>", lambda e, p=part: signal('on_mouse_over_part').send(self, part=p))
            new_image_label.bind("<Button-1>", lambda e, p=part: signal('on_mouse_click_part').send(self, part=p))
