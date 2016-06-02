import pymysql


def connect():
    cxn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", unix_socket=None, autocommit=True)
    cxn.select_db("lego_catalog")
    return cxn


def get_by_weight_from_db_with_threshold(weight, threshold, min_set_qty):
    print('Querying MySql get_by_weight_from_db_with_threshold with weight {}, threshold {}'.format(weight, threshold))

    cxn = connect()
    cursor = cxn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * " \
          "FROM filtered_parts_with_qty " \
          "WHERE weight >= %s AND weight <= %s AND total_qty > %s " \
          "ORDER BY total_qty desc"
    cursor.execute(sql, (weight - threshold, weight + threshold, min_set_qty))
    result = cursor.fetchall()
    cxn.close()

    print('MySql returned {} results'.format(len(result)))

    return result

def get_colors_for_part_number(part_number):
    print('Querying MySql get_colors_for_part with part_number {}'.format(part_number))

    cxn = connect()
    cursor = cxn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT colors.color_id, colors.rgb, colors.color_name, colors.type, COUNT(*) as count_per_color " \
          "FROM inventories " \
          "    JOIN colors ON colors.color_id = inventories.color_id " \
          "WHERE part_number = %s " \
          "GROUP BY inventories.color_id " \
          "ORDER BY count_per_color DESC"
    cursor.execute(sql, (part_number))
    result = cursor.fetchall()
    cxn.close()

    print('MySql returned {} results'.format(len(result)))

    return result