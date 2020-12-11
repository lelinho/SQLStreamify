#!/usr/bin/env python
#Script em Python para criar o banco de dados e alimenta-lo randomicamente

import pymysql as MySQLdb
import random
import time

while True:
    try:
        db = MySQLdb.connect(host='db',user='root',password='password')
        print('CONECTADO!', flush=True)
        break
    except:
        print('DB_LOADING', flush=True)
        time.sleep(3)

mycursor = db.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS sbtest;")
mycursor.execute("USE sbtest;")
mycursor.execute("DROP TABLE IF EXISTS sbtest1;")
db.commit()
mycursor.close()
