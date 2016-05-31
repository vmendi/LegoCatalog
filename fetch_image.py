import tkinter as tk
import io
import os
import requests
from PIL import Image, ImageTk, ImageDraw


def create_part_image_label(part, parent, scale_factor=1.0):
    try:
        image = _fetch_part_image(part['number'])

        if scale_factor != 1:
            image = image.resize((int(image.width * scale_factor), int(image.height * scale_factor)), Image.ANTIALIAS)

        image_tk = ImageTk.PhotoImage(image)

        new_image_label = tk.Label(parent, image=image_tk)
        new_image_label.image_tk = image_tk

    except Exception as exc:
        new_image_label = tk.Label(parent, text=part['number'])

    return new_image_label


def _fetch_part_image(part_number):
    PICTURE_EXTENSION = 'PNG'
    PICTURE_PATH = 'data/PictureCache/{}.{}'

    file_name = PICTURE_PATH.format(part_number, PICTURE_EXTENSION)

    if os.path.isfile(file_name):
        print('Loading image {} from disk cache...'.format(file_name))
        image_ret = Image.open(file_name)
    else:
        try:
            print('Requesting image from Bricklink part_number: {}...'.format(part_number))
            image_ret = _fetch_part_image_from_bricklink(part_number)
        except Exception:
            print('Couldnt fetch image {} from Bricklink. Generating {}...'.format(part_number, file_name))
            image_ret = _generate_image(part_number)

        print('Saving image {} to disk cache...'.format(file_name))
        image_ret.save(file_name, PICTURE_EXTENSION)

    return image_ret


def _generate_image(part_number):
    image_ret = Image.new('RGB', size=(64, 64), color=(255, 255, 255))
    draw = ImageDraw.Draw(image_ret)
    draw.text((5, 25), part_number, fill=(0, 0, 0))
    del draw

    return image_ret


def _fetch_part_image_from_bricklink(part_number):
    response = requests.get(url='http://www.bricklink.com/getPic.asp',
                            headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'},
                            params={'itemType': 'P', 'itemNo': part_number},
                            allow_redirects=True)

    return Image.open(io.BytesIO(response.content))
