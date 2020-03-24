import pymysql as MySQLdb
import configparser
import socket
import pandas as pd
import re
import datetime
from redis import Redis
from pandas.io import sql
from flask import Flask, escape, request

# Le informaçoes do arquivo de configuracao
config = configparser.ConfigParser()
config.read('/config/config.ini')

app = Flask(__name__)    
hostname = socket.gethostname()

redis = Redis("redis")

@app.route("/")
def index():
    return "script_consulta running on {}\n".format(hostname)


@app.route("/<string:consulta>")
def query(consulta):
    
    #buscar query correspondente ao identificador
    sql = config[consulta]['query']

    # Conexão com o Banco de Dados
    db = MySQLdb.connect(config['DB']['host'],config['DB']['user'],config['DB']['password'],config['DB']['db'])
    
    # prepara o cursor
    #cursor = db.cursor()
    e = pd.read_sql(sql,db)
    result_json = e.to_json()

    datahora = str(datetime.datetime.now())
    created = redis.hset(consulta,datahora,result_json)
    
    #cursor.execute(sql)
    #data = cursor.fetchall()
    #result = dict(data)

    # disconnect from server
    db.close()
    return f'{escape(result_json)}'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
