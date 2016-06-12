from tkinter import *
from tkinter.ttk import *
from blinker import signal
from db import get_colors_for_part_number
from PIL import Image, ImageTk

class ColorPicker (Frame):

    COLUMN_COUNT = 10

    def __init__(self, master, for_part):
        Frame.__init__(self, master)

        self.for_part = for_part

        self.inner_frame = Frame(self)
        #self.inner_frame.place(relx=0.5, rely=0, anchor='n')
        self.inner_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.after_idle(self.create_colors)

    def create_colors(self):
        colors = get_colors_for_part_number(self.for_part['number'])

        for index, part_color in enumerate(colors):
            color_frame = Frame(self.inner_frame)
            color_frame.grid(row = int(index / self.COLUMN_COUNT), column = int(index % self.COLUMN_COUNT), pady=5)

            new_color_label = ColorPicker.create_part_color_label(color_frame, (90, 90), part_color['rgb'])
            new_text_label = Label(color_frame, text = part_color['color_name'])

            new_color_label.pack()
            new_text_label.pack()

            new_color_label.bind("<Button-1>", lambda e, p=part_color: self.on_create_part_entry(p))

        cancel_button = Button(self.inner_frame, text = "Cancel", command = self.on_cancel)
        cancel_button.grid(row = int(len(colors) / self.COLUMN_COUNT) + 1, columnspan=self.COLUMN_COUNT)

    def on_create_part_entry(self, part_color):
        signal('on_color_picker_closed').send(self, part=self.for_part, part_color=part_color)
        self.close()

    def on_cancel(self):
        signal('on_color_picker_closed').send(self, part=None, part_color=None)
        self.close()

    def close(self):
        self.place_forget()
        del self

    @staticmethod
    def create_part_color_label(parent, size, part_color_rgb):
        image = Image.new('RGB', size=size, color = "#" + part_color_rgb)
        image_tk = ImageTk.PhotoImage(image)
        new_image_label = Label(parent, image=image_tk)
        new_image_label.image_tk = image_tk
        return new_image_label