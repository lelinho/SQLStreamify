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
mycursor.execute("CREATE DATABASE IF NOT EXISTS placar;")
mycursor.execute("USE placar;")
mycursor.execute("CREATE TABLE IF NOT EXISTS placar (id INT AUTO_INCREMENT PRIMARY KEY, equipe VARCHAR(255), jogador VARCHAR(255), pontos INT)")
mycursor.execute("GRANT ALL ON *.* TO 'root'@'%' IDENTIFIED BY 'password' WITH GRANT OPTION")
mycursor.execute("FLUSH PRIVILEGES;")
db.commit()
mycursor.close()

times = ["New York Knicks", "Golden State Warriors"]
jogadores_1 = ["Kadeem Allen", "Maurice Harkless", "Dennis Smith Jr", "Mitchell Robinson", "Taj Gibson"]
jogadores_2 = ["Stephen Curry", "Jordan Poole", "Klay Thompson", "Kevon Looney", "Draymond Green"]

while True:
  mycursor = db.cursor()
  time.sleep(random.randint(7,20))
  time_pontuador = times[random.randint(0,1)]
  if time_pontuador == "New York Knicks":
    pontuador = jogadores_1[random.randint(0,4)]
  else:
    pontuador = jogadores_2[random.randint(0,4)]
  pontos = random.randint(2,3)
  record_tupla = (time_pontuador, pontuador, pontos)
  insert_query = """INSERT INTO placar (equipe, jogador, pontos) VALUES (%s, %s, %s)"""
  try:
    mycursor.execute(insert_query, record_tupla)
  except mysql.connector.Error as error:
    print("Failed to insert into MySQL table {}".format(error))
  print("Inserido", flush = True)
  db.commit()
  mycursor.close()
