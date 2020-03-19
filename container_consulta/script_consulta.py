import pymysql as MySQLdb
from prettytable import from_db_cursor

# Open database connection
db = MySQLdb.connect("172.17.0.1","zabbix","z@bb1x","zabbix" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

cursor.execute("SELECT * FROM history_uint WHERE itemid=27456 ORDER BY clock DESC limit 5")
data = from_db_cursor(cursor)

print(data)

# disconnect from server
db.close()