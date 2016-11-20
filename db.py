from collections import defaultdict
from decimal import Decimal
import pymysql


def connect():
    cxn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", unix_socket=None, autocommit=True)
    cxn.select_db("lego_catalog")
    return cxn


def get_by_part_number(current_part_number_filter):
    print('Querying MySql get_by_part_number with current_part_number_filter {}'.format(current_part_number_filter))

    cxn = connect()
    cursor = cxn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * " \
          "FROM filtered_parts_with_qty " \
          "LEFT JOIN weighings_clusters on weighings_clusters.part_number = filtered_parts_with_qty.number " \
          "LEFT JOIN ordering on ordering.number = filtered_parts_with_qty.number " \
          "WHERE filtered_parts_with_qty.number LIKE %s " \
          "ORDER BY total_qty desc"
    cursor.execute(sql, current_part_number_filter + '%')
    parts_list = cursor.fetchall()
    cursor.close()
    cxn.close()

    print('MySql returned {} results'.format(len(parts_list)))

    attach_clusters_to_parts(parts_list)
    parts_list = uniqfy_parts(parts_list)

    print('After deduping we have {} results'.format(len(parts_list)))

    return parts_list


def get_by_weight_from_db_with_threshold(weight, threshold, min_set_qty):
    print('Querying MySql get_by_weight_from_db_with_threshold with weight {}, threshold {}'.format(weight, threshold))

    cxn = connect()
    cursor = cxn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * " \
          "FROM filtered_parts_with_qty " \
          "LEFT JOIN weighings_clusters on weighings_clusters.part_number = filtered_parts_with_qty.number " \
          "LEFT JOIN ordering on ordering.number = filtered_parts_with_qty.number " \
          "WHERE IFNULL(weighings_clusters.mean_weight, filtered_parts_with_qty.weight) >= %s " \
          "AND IFNULL(weighings_clusters.mean_weight, filtered_parts_with_qty.weight) < %s AND total_qty > %s " \
          "ORDER BY total_qty desc"
    cursor.execute(sql, (weight - threshold, weight + threshold, min_set_qty))
    parts_list = cursor.fetchall()
    cursor.close()
    cxn.close()

    print('MySql returned {} results'.format(len(parts_list)))

    # We want to include information about the molds (clusters) a part belongs to
    attach_clusters_to_parts(parts_list)

    # The lack and imposibility in MySQL of a GROUP BY in the query above means that we have to dedup here.
    # The imposibility is derived from the fact we want to SELECT *
    parts_list = uniqfy_parts(parts_list)

    print('After deduping we have {} results'.format(len(parts_list)))

    return parts_list


# Append to each part a list of all the clusters (molds) than it's been seen in
def attach_clusters_to_parts(parts_list):
    grouped_parts = defaultdict(list)

    for individual_part in parts_list:
        grouped_parts[individual_part['number']].append(individual_part)

    for part_number, group in grouped_parts.items():
        clusters = []
        for individual_part in group:
            if individual_part['weighing_cluster_id']:
                clusters.append({'weighing_cluster_id': individual_part['weighing_cluster_id'],
                                 'mean_weight': individual_part['mean_weight'],
                                 'weighings_count': individual_part['weighings_count']})
        for individual_part in group:
            individual_part['clusters'] = clusters


# Returns a new list removing duplicated parts
def uniqfy_parts(parts_list):
    seen = set()
    ret = []
    for individual_part in parts_list:
        if not individual_part['number'] in seen:
            ret.append(individual_part)
            seen.add(individual_part['number'])
    return ret


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


def get_closest_cluster(part_number, weight):
    cxn = connect()
    cursor = cxn.cursor(pymysql.cursors.DictCursor)

    cluster_threshold = get_cluster_threshold(weight)

    sql = "SELECT * " \
          "FROM weighings_clusters " \
          "WHERE part_number = %s " \
          "AND mean_weight >= %s AND mean_weight <= %s "

    cursor.execute(sql, (part_number, weight - cluster_threshold, weight + cluster_threshold))
    result = cursor.fetchall()

    if len(result) == 0:
        return None

    cluster = result[0]

    if len(result) > 1:
        print('Clustering error, {} clusters'.format(len(result)))
        min_dist = Decimal('99999')
        # Pick out the closest cluster
        for curr_cluster in result:
            curr_dist = abs(curr_cluster['mean_weight'] - weight)
            if curr_dist < min_dist:
                cluster = curr_cluster
                min_dist = curr_dist

    cursor.close()
    cxn.close()

    return cluster


def get_cluster_threshold(for_weight):
    return for_weight * Decimal('0.03')    # Accept 3% tolerance


def insert_weighing(part_number, color_id, weight, threshold):
    print('Inserting weighing {}, {}, {}, {}'.format(part_number, color_id, weight, threshold))

    cluster = get_closest_cluster(part_number, weight)

    cxn = connect()
    cursor = cxn.cursor(pymysql.cursors.DictCursor)

    if not cluster:
        print("Creating weighing cluster")

        sql = "INSERT INTO weighings_clusters (part_number, mean_weight, weighings_count) " \
              "VALUES (%s, %s, %s)"

        cursor.execute(sql, (part_number, weight, 1))
        weighing_cluster_id = cursor.lastrowid
        print("Weighing cluster created with weighing_cluster_id {}".format(weighing_cluster_id))
    else:
        weighing_cluster_id = cluster['weighing_cluster_id']
        prev_mean_weight = Decimal(cluster['mean_weight'])
        prev_weighings_count = cluster['weighings_count']

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

    cursor.execute(sql, (part_number, color_id, weight, threshold, weighing_cluster_id, get_cluster_threshold(weight)))

    cursor.close()
    cxn.close()