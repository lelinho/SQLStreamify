import pymysql as MySQLdb
from prettytable import from_db_cursor
from flask import Flask, escape, request

# Open database connection
db = MySQLdb.connect("172.17.0.1","zabbix","z@bb1x","zabbix" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

cursor.execute("SELECT * FROM history_text WHERE itemid=59197 ORDER BY clock DESC limit 5")
data = from_db_cursor(cursor)

# disconnect from server
db.close()

app = Flask(__name__)
@app.route('/')
def print():
    return f'{escape(data)}'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


