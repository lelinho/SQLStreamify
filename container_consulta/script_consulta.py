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
import json
import pika
from redis import Redis
from flask import Flask, escape, request, jsonify
from jsondiff import diff

# Le informaçoes do arquivo de configuracao
config = configparser.ConfigParser()
config.read('/config/config.ini')

# informações sobre o script
app = Flask(__name__)
hostname = socket.gethostname()

# conexão com o redis
redis = Redis("redis")


def publicaMQTT(consulta, publicacao):
    ###############################
    # publicacao por MQTT         #
    ###############################

    # conexão com o MQTT utilizando pika(RabbitMQ)
    conexao_mqtt = pika.BlockingConnection(
        pika.ConnectionParameters('mqtt'))
    canal = conexao_mqtt.channel()

    # seta o canal de conexão do MQTT
    canal.queue_declare(queue=consulta)

    # publica a alteraçao
    canal.basic_publish(exchange='',
                        routing_key=consulta,
                        body=publicacao)

    # fecha a conexao do mqtt
    conexao_mqtt.close()


def ultimoResultado(consulta):
    ultimo = redis.hget(consulta, "resultado")
    if ultimo:
        ultimo = ultimo.decode("utf-8")
    else:
        ultimo = "[]"
    return ultimo


def comparaResultados(consulta1, consulta2):
    # utilizando o jsondiff
    return diff(consulta1, consulta2, load=True, dump=True)


@app.route("/")
def index():
    return "script_consulta running on {}\n".format(hostname)


@app.route("/<string:consulta>")
def query(consulta):
    # buscar query correspondente ao identificador
    sql = config[consulta]['query']

    # Especificaçoes da query
    modo = "full_dataset"
    if config.has_option(consulta, 'modo'):
        if config[consulta]['modo'] == "one_at_time":
            modo = "one_at_time"

    # busca resultado da ultima consulta gravada
    ultimo = ultimoResultado(consulta)
    print("****** Ultimo ********", flush=True)
    print(ultimo, flush=True)

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
            print("****** Diff ********", flush=True)
            print(diff, flush=True)
            diff_loaded = json.loads(diff)
            for i in diff_loaded:
                # verificar se é lista - primeiro diff
                if isinstance(diff_loaded, list):
                    item_loaded = i
                    print("****** item_loaded_ ********", flush=True)
                    print(i, flush=True)
                    redis.hincrby(consulta, "count", 1)
                    result_diff = json.dumps(i)
                    publicaMQTT(consulta, result_diff)
                else:
                    # senao:
                    item_loaded = diff_loaded[i]
                    print("****** item_loaded ********", flush=True)
                    print(item_loaded, flush=True)
                    for x in item_loaded:
                        print("****** X ********", flush=True)
                        print(x, flush=True)
                        redis.hincrby(consulta, "count", 1)
                        print("****** x[1] ********", flush=True)
                        print(x[1], flush=True)
                        result_diff = json.dumps(x[1])
                        publicaMQTT(consulta, result_diff)

                #publicaMQTT(consulta, json.dumps(diff))
        print("Alterado e publicado!", flush=True)

    # desconecta do servidor
    db.close()
    return result_json


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
