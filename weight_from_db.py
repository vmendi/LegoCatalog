import io
import os
import pymysql
import requests
from PIL import Image, ImageDraw
from db import connect


def get_by_weight_from_db_with_threshold(weight, threshold):
    print('Querying MySql with weight {}, threshold {}'.format(weight, threshold))

    cxn = connect()
    cursor = cxn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * " \
          "FROM filtered_parts_with_qty " \
          "WHERE weight >= %s AND weight <= %s " \
          "ORDER BY total_qty desc"
    cursor.execute(sql, (weight - threshold, weight + threshold))
    result = cursor.fetchall()
    cxn.close()

    print('MySql returned {} results'.format(len(result)))

    return result


def fetch_part_image(part_number):
    PICTURE_EXTENSION = 'PNG'
    PICTURE_PATH = 'data/PictureCache/{}.{}'

    file_name = PICTURE_PATH.format(part_number, PICTURE_EXTENSION)

    if os.path.isfile(file_name):
        print('Loading image {} from disk cache...'.format(file_name))
        image_ret = Image.open(file_name)
    else:
        try:
            image_ret = fetch_part_image_from_bricklink(part_number)
        except Exception as exc:
            print('Couldnt fetch image {} from Bricklink. Generating {}...'.format(part_number, file_name))
            image_ret = Image.new('RGB', size=(64, 64), color=(255, 255, 255))
            draw = ImageDraw.Draw(image_ret)
            draw.text((5, 25), part_number, fill=(0, 0, 0))
            del draw

        print('Saving image {} to disk cache...'.format(file_name))
        image_ret.save(file_name, PICTURE_EXTENSION)

    return image_ret


def fetch_part_image_from_bricklink(part_number):
    print('Requesting image from Bricklink part_number: {}...'.format(part_number))

    response = requests.get(url='http://www.bricklink.com/getPic.asp',
                            headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'},
                            params={'itemType': 'P', 'itemNo': part_number},
                            allow_redirects=True)

    return Image.open(io.BytesIO(response.content))