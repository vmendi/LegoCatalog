from decimal import Decimal
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
    cursor.close()
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
    cursor.close()
    cxn.close()

    print('MySql returned {} results'.format(len(result)))

    return result

def insert_weighing(part_number, color_id, weight, threshold):
    print('Inserting weighing {}, {}, {}, {}'.format(part_number, color_id, weight, threshold))

    cluster_threshold = weight * Decimal('0.05')    # Accept 5% tolerance

    cxn = connect()
    cursor = cxn.cursor(pymysql.cursors.DictCursor)

    # Obtain the closest cluster
    sql = "SELECT * " \
          "FROM weighings_clusters " \
          "WHERE part_number = %s " \
          "AND mean_weight >= %s AND mean_weight <= %s "

    cursor.execute(sql, (part_number, weight - cluster_threshold, weight + cluster_threshold))
    result = cursor.fetchall()

    if len(result) == 0:
        print("Creating weighing cluster")

        sql = "INSERT INTO weighings_clusters (part_number, mean_weight, weighings_count) " \
              "VALUES (%s, %s, %s)"

        cursor.execute(sql, (part_number, weight, 1))
        weighing_cluster_id = cursor.lastrowid
        print("Weighing cluster created with weighing_cluster_id {}".format(weighing_cluster_id))
    else:
        if len(result) > 1:
            print('Clustering error, {} clusters'.format(len(result)))

        weighing_cluster_id = result[0]['weighing_cluster_id']
        prev_mean_weight = Decimal(result[0]['mean_weight'])
        prev_weighings_count = result[0]['weighings_count']

        print("Updating weighing cluster with weighing_cluster_id {}, mean_weight {}, weighings_count {}"
                .format(weighing_cluster_id, prev_mean_weight, prev_weighings_count))

        sql = "UPDATE weighings_clusters " \
              " SET mean_weight = %s, " \
              "     weighings_count = %s " \
              " WHERE weighing_cluster_id = %s"

        res = cursor.execute(sql, ((prev_mean_weight + weight) / Decimal('2.0'), prev_weighings_count + 1, weighing_cluster_id))
        print("UPDATE weighings_clusters returned {}".format(res))

    # Insert the weighing
    sql = "INSERT INTO weighings (part_number, color_id, weight, threshold, weighing_cluster_id, cluster_threshold) " \
          "VALUES (%s, %s, %s, %s, %s, %s)"

    cursor.execute(sql, (part_number, color_id, weight, threshold, weighing_cluster_id, cluster_threshold))

    cursor.close()
    cxn.close()
