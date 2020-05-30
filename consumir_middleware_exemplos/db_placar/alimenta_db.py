#!/usr/bin/env python
#Script em Python para criar o banco de dados e alimenta-lo randomicamente

import mysql.connector

mydb = mysql.connector.connect(
  host="db",
  user="",
  passwd="",
  database="placar"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")