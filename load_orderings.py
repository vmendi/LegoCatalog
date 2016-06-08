import db
import os
import pymysql


# To load a csv file that contains the orderings table, just execute this file with:
#  $ python load_orderings.py

# The idea is that the source of truth is a google sheet that somebody mantains. It can have any number of columns, but
# only the first and second column will be inserted by this script as (number, ordering).

# The google sheet was created by hand by a chunk of code in LegoCatalog.sql, section "Ordering Table"

cxn = db.connect()

cursor = cxn.cursor(pymysql.cursors.DictCursor)

sql = "DROP TABLE IF EXISTS ordering"
print(sql)
cursor.execute(sql)

sql = """
create table ordering (
	number VARCHAR(32) PRIMARY KEY,
	ordering VARCHAR(64)
)
"""
print(sql)
cursor.execute(sql)

sql = """
LOAD DATA INFILE '{}/data/Csv/Lego - Ordering.csv' INTO TABLE ordering
	FIELDS TERMINATED BY ','  LINES TERMINATED BY '\r\n'
	(number, ordering)
"""

sql = sql.format(os.getcwd())
print(sql)
cursor.execute(sql)

cxn.close()
