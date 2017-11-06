from tkinter import *
from tkinter import font
from blinker import signal
import fetch_image


class PartImagesGrid (Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bd = 1, relief=SUNKEN)

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

        signal('on_new_weight').connect(self.on_new_weight)
        signal('on_new_part_number_filter').connect(self.on_new_part_number_filter)

        self.canvas.bind('<Enter>', self.bound_to_mousewheel)
        self.canvas.bind('<Leave>', self.unbound_to_mousewheel)

    def bound_to_mousewheel(self, event):
        signal("on_mouse_global_wheel").connect(self.on_mouse_wheel)

    def unbound_to_mousewheel(self, event):
        signal("on_mouse_global_wheel").disconnect(self.on_mouse_wheel)

    def on_mouse_wheel(self, sender, mouse_event):
        self.canvas.yview_scroll(-mouse_event.delta, "units")

    def on_inner_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width() - 7)

    def destroy_grid(self):
        for widget in self.image_widgets:
            widget.destroy()

        self.image_widgets = []

    def on_new_weight(self, sender, weight, window_center, threshold, parts):
        self.destroy_grid()

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

    def on_new_part_number_filter(self, sender, part_number, parts):
        self.on_new_weight(sender, 0, 0, 0, parts)  # We can send 0, 0, 0 because they are unused
