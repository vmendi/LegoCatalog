import tkinter as tk
from tkinter import font
from blinker import signal
import webbrowser
import db
import fetch_image


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

        parts = db.get_by_weight_from_db_with_threshold(current_weight, current_threshold)

        for part in parts:
            new_frame = tk.Frame(self)

            # Image
            new_image_label = fetch_image.create_image_label(part, new_frame)
            new_image_label.pack()

            # URL link
            new_url_label = tk.Label(new_frame, text=part['number'], fg='blue', cursor='draft_large',
                                     font=font.Font(family="Helvetica", size=12))
            new_url_label.pack()

            # Add to grid
            new_frame.grid(row=int(len(self.image_widgets) / 10), column=int(len(self.image_widgets) % 10))
            self.image_widgets.append(new_frame)

            # Emit events
            url = 'http://alpha.bricklink.com/pages/clone/catalogitem.page?P=%s' % part['number']
            new_url_label.bind("<Button-1>", lambda e, u=url: webbrowser.open_new(u))
            new_frame.bind("<Enter>", lambda e, p=part: signal('on_mouse_over_part').send(self, part=p))
            new_image_label.bind("<Button-1>", lambda e, p=part: signal('on_mouse_click_part').send(self, part=p))
