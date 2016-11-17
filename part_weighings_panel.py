from tkinter import *
from blinker import signal


class PartWeighingsPanel(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bd=1, relief='sunken')

        self.grid_columnconfigure(0, weight=1)
        self.part_weighings_widgets = []

        signal('on_mouse_over_part').connect(self.on_mouse_over_part)

    def on_mouse_over_part(self, sender, part):
        for widget in self.part_weighings_widgets:
            widget.destroy()

        cluster_count = len(part['clusters'])

        if cluster_count > 0:
            row_count = 0
            for cluster in part['clusters']:
                cluster_frame = Frame(self)
                self.part_weighings_widgets.append(cluster_frame)

                if row_count != 0:
                    separator = Frame(self, height=2, bd=1, relief='sunken')
                    separator.grid(row=row_count, column=0, columnspan=2, sticky='we')
                    self.part_weighings_widgets.append(separator)
                    row_count += 1

                cluster_mean_weight_text = Label(cluster_frame, text='Mold weight:')
                cluster_mean_weight_text.grid(row=1, column=0, sticky='w')
                cluster_frame.columnconfigure(1, weight=1)
                cluster_mean_weight = Label(cluster_frame, text=cluster['mean_weight'])
                cluster_mean_weight.grid(row=1, column=1, sticky='e')

                cluster_weighings_count_text = Label(cluster_frame, text='Weighings count:')
                cluster_weighings_count_text.grid(row=2, column=0, sticky='w')
                cluster_weighings_count = Label(cluster_frame, text=cluster['weighings_count'])
                cluster_weighings_count.grid(row=2, column=1, sticky='e')

                cluster_frame.grid(row=row_count, column=0, sticky='we', pady=5)
                row_count += 1
        else:
            title_text = Label(self, text='From Bricklink:')
            self.part_weighings_widgets.append(title_text)
            title_text.grid(row=0, column=0, sticky='w', pady=5)

            weight_text = Label(self, text=str(part['weight']))
            self.part_weighings_widgets.append(weight_text)
            weight_text.grid(row=0, column=1, sticky='e', pady=5)

