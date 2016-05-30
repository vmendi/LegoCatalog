#from tkinter.ttk import *
from tkinter import *
from blinker import signal
from db import get_colors_for_part_number
from PIL import Image, ImageTk

class ColorPicker (Frame):

    COLUMN_COUNT = 10

    def __init__(self, master, for_part):
        Frame.__init__(self, master)

        self.inner_frame = Frame(self)
        #self.inner_frame.place(relx=0.5, rely=0, anchor='n')
        self.inner_frame.place(relx=0.5, rely=0.5, anchor='center')

        colors = get_colors_for_part_number(for_part['number'])

        for index, part_color in enumerate(colors):
            color_frame = Frame(self.inner_frame)
            color_frame.grid(row = int(index / self.COLUMN_COUNT), column = int(index % self.COLUMN_COUNT), pady=5)

            image = Image.new('RGB', size=(128, 128), color = "#" + part_color['rgb'])
            image_tk = ImageTk.PhotoImage(image)

            new_image_label = Label(color_frame, image=image_tk)
            new_image_label.image_tk = image_tk

            new_label = Label(color_frame, text = part_color['color_name'])

            new_image_label.pack()
            new_label.pack()

            new_image_label.bind("<Button-1>", lambda e, p=part_color: self.on_create_part_entry(for_part, p))

        cancel_button = Button(self.inner_frame, text = "Cancel", command = self.close)
        cancel_button.grid(row = int(len(colors) / self.COLUMN_COUNT) + 1, columnspan=self.COLUMN_COUNT)


    def on_create_part_entry(self, part, part_color):
        signal('on_create_part_entry').send(self, part=part, part_color=part_color)
        self.close()

    def close(self):
        self.place_forget()
        del self