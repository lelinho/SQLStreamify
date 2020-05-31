#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Verifica eventos nas tabelas relacionadas a busca
#
import socket
import configparser
import requests
import json
import re
from datetime import datetime
from redis import Redis
from flask import Flask, Response
from moz_sql_parser import parse
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)

config = configparser.ConfigParser()
config.read('/config/config.ini')

MYSQL_SETTINGS = {
    "host": config['DB']['host'],
    "port": int(config['DB']['port']),
    "user": config['DB']['user'],
    "passwd": config['DB']['password']
}

app = Flask(__name__)
hostname = socket.gethostname()

redis = Redis("redis")


def identificaWhere(query):
    # buscar query correspondente ao identificador gravada no Redis
    sql_str = redis.hget("queries", query).decode('utf-8')    
    parsed = parse(sql_str)

    where = None
    if "where" in parsed:
        where = parsed["where"]

    return where


def identificaTabelas(query):
    # buscar query correspondente ao identificador
    sql_str = redis.hget("queries", query).decode('utf-8') 

    try:
        parsed = parse(sql_str)
    except:
        print("Erro no parse do SQL", flush=True)

    table = []
    tabelas = parsed["from"]

    if type(tabelas) == str:
        table.append(tabelas)
    else:
        for conteudo in tabelas:
            #print(conteudo, flush=True)
            if "value" in conteudo:
                #print(conteudo["value"], flush=True)
                table.append(conteudo["value"])
            else:
                a = [value for key, value in conteudo.items()
                     if 'join' in key.lower()]
                if a:
                    #print(a[0], flush=True)
                    if "value" in a[0]:
                        #print(a[0]["value"], flush=True)
                        table.append(a[0]["value"])

    print(table, flush=True)
    return table


def verificaRequisitos(where, linha_binlog, query):
    if where:
        #print(where, flush=True)
        # {'and': [{'eq': ['itemid', 53939]}, {'gt': ['clock', 1586801554]}]}

        # busca por igualdades no where
        equal = re.findall(r'\'eq\':(.*?)}', str(where))
        for eq in equal:
            # transforma a string em uma lista
            eq = eval(eq)
            #print(eq, flush=True)
            #print(eq[0], flush=True)
            if linha_binlog[eq[0]] == eq[1]:
                r = requests.get("http://lbconsulta/" + query)
    else:
        r = requests.get("http://lbconsulta/" + query)


@app.route("/")
def index():
    return "log_eventos running on {}\n".format(hostname)


@app.route("/<string:query>/<int:server_id>")
def eventos(query, server_id):

    # buscar query correspondente ao identificador
    # busca tabelas afetadas pela consulta
    tabelas = identificaTabelas(query)

    # busca condições
    where = identificaWhere(query)

    # Monitora eventos das tabelas que fazem parte da consulta

    # server_id is your slave identifier, it should be unique.
    # set blocking to True if you want to block and wait for the next event at
    # the end of the stream
    stream = BinLogStreamReader(connection_settings=MYSQL_SETTINGS,
                                server_id=server_id,
                                only_events=[DeleteRowsEvent,
                                             WriteRowsEvent, UpdateRowsEvent],
                                only_tables=tabelas,
                                # skip_to_timestamp: busca apenas novos eventos, ignora logs antigos...
                                skip_to_timestamp=datetime.timestamp(
                                    datetime.now()),
                                blocking=True)
    #contador = 0

    # Realiza uma primeira busca antes de começar a consultar apenas quando tiver eventos...
    r = requests.get("http://lbconsulta/" + query)

    for binlogevent in stream:
        # binlogevent.dump()
        #contador = contador + 1
        # print(contador)
        for row in binlogevent.rows:
            #print(row, flush=True)
            if isinstance(binlogevent, WriteRowsEvent):
                # FAZER A VERIFICAÇÃO DO WHERE
                verificaRequisitos(where, row["values"], query)
            if isinstance(binlogevent, UpdateRowsEvent):
                #print(row, flush=True)
                verificaRequisitos(where, row["before_values"], query)

    stream.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
