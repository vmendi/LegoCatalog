import pymysql


def connect():
    cxn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", unix_socket=None, autocommit=True)
    cxn.select_db("lego_catalog")
    return cxn


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
