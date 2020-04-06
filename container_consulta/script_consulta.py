import pymysql as MySQLdb
import configparser
import socket
import re
import datetime
import json
import pika
from redis import Redis
from flask import Flask, escape, request, jsonify
from deepdiff import DeepDiff

# Le informaçoes do arquivo de configuracao
config = configparser.ConfigParser()
config.read('/config/config.ini')

#informações sobre o script
app = Flask(__name__)    
hostname = socket.gethostname()

#conexão com o redis
redis = Redis("redis")

def ultimoResultado(consulta):
    ultimo = redis.hget(consulta, "resultado")
    if ultimo:
        ultimo = ultimo.decode("utf-8")
    return ultimo

def comparaResultados(consulta1, consulta2):
    diff = DeepDiff(consulta1, consulta2)
    #if diff:
        #print(diff, flush=True)        
    return diff


@app.route("/")
def index():
    return "script_consulta running on {}\n".format(hostname)


@app.route("/<string:consulta>")
def query(consulta):    
    #buscar query correspondente ao identificador
    sql = config[consulta]['query']

    #busca resultado da ultima consulta gravada
    ultimo = ultimoResultado(consulta)

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
    
    result_json = json.dumps(json_data)

    # Compara os resultados
    # do ultimo armazenado em memória, e do buscado agora
    diff = comparaResultados(ultimo, result_json)
    if diff:
        created = redis.hset(consulta,"resultado",result_json)
        redis.hincrby(consulta,"count", 1)
        print("Alterado e publicado!", flush=True)        
        ###############################
        # publicacao por MQTT         #
        ###############################
        
        #conexão com o MQTT utilizando pika(RabbitMQ)
        conexao_mqtt = pika.BlockingConnection(pika.ConnectionParameters('mqtt'))
        canal = conexao_mqtt.channel()
        
        #seta o canal de conexão do MQTT
        canal.queue_declare(queue=consulta)

        #publica a alteraçao
        canal.basic_publish(exchange='',
                            routing_key = consulta,
                            body = result_json)
        
        #fecha a conexao do mqtt
        conexao_mqtt.close()

    # disconnect from server
    db.close()
    return result_json

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
