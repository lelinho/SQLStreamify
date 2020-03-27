import pymysql as MySQLdb
import configparser
import socket
import re
import datetime
from redis import Redis
from flask import Flask, escape, request, jsonify

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
    cursor = db.cursor()
    
    cursor.execute(sql)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    data = cursor.fetchall()
    json_data=[]
    for result in data:
        json_data.append(dict(zip(row_headers,result)))
    
    result_json = jsonify(json_data)
    #print(json_data)
    #print(result_json)

    datahora = str(datetime.datetime.now())
    #created = redis.hset(consulta,datahora,result_json)

    # disconnect from server
    db.close()
    return result_json


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
