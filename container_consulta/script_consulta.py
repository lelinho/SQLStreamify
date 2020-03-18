import pymysql as MySQLdb

# Open database connection
db = MySQLdb.connect("172.17.0.1","zabbix","z@bb1x","zabbix" )

# prepare a cursor object using cursor() method
cursor = db.cursor()


cursor.execute("SELECT * FROM history_uint WHERE itemid=64431 ORDER BY clock DESC limit 30")
data = cursor.fetchall()

for row in data:
    print(row[0])


# disconnect from server
db.close()