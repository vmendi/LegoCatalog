import tkinter as tk
from tkinter import font
import webbrowser
from PIL import ImageTk
from blinker import signal
from weight_from_db import get_by_weight_from_db_with_threshold, fetch_part_image


class PartImagesGrid (tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.image_widgets = []

    def destroy_grid(self):
        for widget in self.image_widgets:
            widget.destroy()

        self.image_widgets = []

    def create_grid(self, current_weight, current_threshold):
        self.destroy_grid()

        parts = get_by_weight_from_db_with_threshold(current_weight, current_threshold)

        for part in parts:
            new_frame = tk.Frame(self)

            new_frame.bind("<Enter>", lambda e, part=part: signal('on_mouse_over_part').send(self, part=part))

            new_image_label = self.create_image_label(part, new_frame)
            new_image_label.pack()

            # url link
            new_url_label = tk.Label(new_frame, text=part['number'], fg='blue', cursor='draft_large',
                                     font=font.Font(family="Helvetica", size=12))
            new_url_label.pack()
            url_link = 'http://alpha.bricklink.com/pages/clone/catalogitem.page?P=%s' % part['number']
            self.bind_url_label(new_url_label, url_link)

            # Add to grid. TODO: how to resize the grid dinamically
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
