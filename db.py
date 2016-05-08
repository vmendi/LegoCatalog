import pymysql


def connect():
    cxn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", unix_socket=None, autocommit=True)
    cxn.select_db("lego_catalog")
    return cxn