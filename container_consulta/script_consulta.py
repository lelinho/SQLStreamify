#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Executa a consulta no Banco de Dados e grava em memória o resultado
#

import pymysql as MySQLdb
import configparser
import socket
import re
import datetime
import simplejson as json
import pika
import subprocess
from redis import Redis
from flask import Flask, escape, request, jsonify
from jsondiff import diff

# Le informaçoes do arquivo de configuracao
config = configparser.ConfigParser()
config.read('/config/config.ini')

# informações sobre o script
app = Flask(__name__)
hostname = socket.gethostname()

#busca o hostname do container em execução para guardar o histórico da execução
bashCommand = """curl -s -XGET --unix-socket /var/run/docker.sock -H "Content-Type: application/json" http://v1.24/containers/$(hostname)/json | jq -r .Name[1:]"""
subprocess = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
hostname_cont = subprocess.stdout.read()
hostname_cont = hostname_cont.rstrip()

# conexão com o redis
redis = Redis("redis")


def publicaMQTT(consulta, publicacao):
    """
    Realiza uma publicação na exchange "consulta" com o contéudo "publicação".

    :param consulta: nome da exchange
    :param publicacao: conteúdo da publicação
    """
    ###############################
    # publicacao por MQTT         #
    ###############################

    # conexão com o MQTT utilizando pika(RabbitMQ)
    conexao_mqtt = pika.BlockingConnection(
        pika.ConnectionParameters('mqtt'))
    canal = conexao_mqtt.channel()

    # utilizando o exchange com o nome da query
    canal.exchange_declare(exchange=consulta, exchange_type='fanout')

    # publica a alteraçao
    canal.basic_publish(exchange=consulta,
                        routing_key='',
                        body=publicacao)

    # fecha a conexao do mqtt
    conexao_mqtt.close()


def ultimoResultado(consulta):
    """
    Retorna o último resultado da consulta, passada como parâmetro, armazenado no banco de dados em memória principal.

    :param consulta: nome da consulta

    :return: último resultado da consulta
    """

    ultimo = redis.hget(consulta, "resultado")
    if ultimo:
        ultimo = ultimo.decode("utf-8")
    else:
        ultimo = "[]"
    return ultimo


def comparaResultados(consulta1, consulta2):
    """
    Compara e retorna o resultado da diferença entre duas consultas.

    :param consulta1: primeiro resultado da consulta a ser comparado
    :param consulta2: segundo resultado da consulta a ser comparado
    
    :return: diferença entre as consultas
    """


    # utilizando o jsondiff
    return diff(consulta1, consulta2, load=True, dump=True)


@app.route("/")
def index():
    """
    Respondendo na rota padrão "/", retorna por HTTP a mensagem em qual host está sendo executado o serviço.
    """
    
    return "script_consulta running on {}\n".format(hostname)


@app.route("/<string:consulta>")
def query(consulta):
    """
    Respondendo na rota "/nome_da_consulta". É através desta rota que são realizadas as consultas.
    Primeiramente de acordo com a estrutura do SQLStreamify a requisição é feita ao loadbalancer de consultas que repassa a requisição à instância livre do conteineires através de um balancemaneto round robin.

    É retornado o json com a mensagem da consulta, além disso é realizada a publicação na exchange com o nome da consulta com a mensagem obtida. Para consumo das aplicações que assinam esta consulta.

    :param <string:consulta> nome da consulta
    """    
    # buscar query correspondente ao identificador
    sql = redis.hget("queries", consulta).decode('utf-8')    
    
    # Especificaçoes da query - alterar para buscar no banco
    modo = redis.hget(consulta, "modo").decode('utf-8')

    # busca resultado da ultima consulta gravada
    ultimo = ultimoResultado(consulta)
    #print("****** Ultimo ********", flush=True)
    #print(ultimo, flush=True)

    # adiciona informações de execução do docker
    print(hostname_cont, flush=True)
    host = redis.hset(consulta, "container_consulta", hostname_cont) #hostname do último container que executou a consulta
    redis.hincrby(consulta, "check-alive-consulta", 1) #incrementa um contador de check-alive

    # Conexão com o Banco de Dados
    db = MySQLdb.connect(config['DB']['host'], config['DB']
                         ['user'], config['DB']['password'], config['DB']['db'])

    # prepara o cursor
    cursor = db.cursor()

    cursor.execute(sql)
    # extrai os nomes dos campos
    row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()
    json_data = []
    for result in data:        
        json_data.append(dict(zip(row_headers, result)))

    result_json = json.dumps(json_data)

    # Compara os resultados
    # do ultimo armazenado em memória, e do buscado agora
    diff = comparaResultados(ultimo, result_json)
    if diff:
        # No modo "full_dataset" o dataset completo é enviado a cada alteração nos dados.
        if modo == "full_dataset":
            created = redis.hset(consulta, "resultado", result_json)
            redis.hincrby(consulta, "count", 1)
            publicaMQTT(consulta, result_json)
        # No modo "one_at_time" cada registro da consulta é retornado um por vez, para montagem e atualização do dataset
        if modo == "one_at_time":
            created = redis.hset(consulta, "resultado", result_json)
            print(diff, flush=True)
            diff_loaded = json.loads(diff)
            for i in diff_loaded:
                # verificar se é lista - primeiro diff
                if isinstance(diff_loaded, list):
                    item_loaded = i
                    redis.hincrby(consulta, "count", 1)
                    json_data = []
                    json_data.append(i)
                    result_diff = json.dumps(json_data)
                    publicaMQTT(consulta, result_diff)

                else:
                    # senao:
                    item_loaded = diff_loaded[i]
                    for x in item_loaded:
                        redis.hincrby(consulta, "count", 1)
                        json_data = []
                        #/verificar ->>> 
                        json_data.append(x[1])
                        result_diff = json.dumps(json_data)
                        publicaMQTT(consulta, result_diff)



                #publicaMQTT(consulta, json.dumps(diff))
        print("Alterado e publicado!", flush=True)

    # desconecta do servidor
    db.close()
    return result_json


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
    #app.run(host="0.0.0.0", port=80)
