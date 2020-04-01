#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Verifica eventos
#
from flask import Flask, Response
import socket
import configparser
import re
import requests
import sqlparse
import json
from moz_sql_parser import parse
from time import perf_counter
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


def identificaWhere(query):
    #buscar query correspondente ao identificador
    sql_str = config[query]['query']
    parsed = parse(sql_str)
    
    where = None
    if "where" in parsed:
        where = parsed["where"]
    
    return where



def identificaTabelas(query):
    #buscar query correspondente ao identificador
    sql_str = config[query]['query']    

    try:
        parsed = parse(sql_str)
    except:
        print("Erro no parse do SQL", flush=True)

    table = []
    tabelas = parsed["from"]

    for conteudo in tabelas:
        #print(conteudo, flush=True)
        if "value" in conteudo:
            #print(conteudo["value"], flush=True)
            table.append(conteudo["value"])
        else:
            a = [value for key, value in conteudo.items() if 'join' in key.lower()]
            if a:
                #print(a[0], flush=True)
                if "value" in a[0]:
                    #print(a[0]["value"], flush=True)
                    table.append(a[0]["value"])

    return table


def verificaRequisitos(where, linha_binlog, query):    
    if where:
        for statement in where.items():            
            #print(statement[0], flush = True)
            #print(linha_binlog[statement[1][0]], flush=True)
            #print(statement[1][1], flush=True)

            #MONTAR PARA AS OUTRAS OPERAÇÕES SQL
            if statement[0] == "eq":
                if linha_binlog[statement[1][0]] == statement[1][1]:                    
                    r = requests.get("http://lbconsulta/" + query)
    else:
        r = requests.get("http://lbconsulta/" + query)


@app.route("/")
def index():
    return "log_eventos running on {}\n".format(hostname)


@app.route("/<string:query>")
def eventos(query):

    #buscar query correspondente ao identificador
    
    #busca tabelas afetadas pela consulta
    tabelas = identificaTabelas(query)

    #busca condições
    where = identificaWhere(query)

    # Monitora eventos das tabelas que fazem parte da consulta

    # server_id is your slave identifier, it should be unique.
    # set blocking to True if you want to block and wait for the next event at
    # the end of the stream
    stream = BinLogStreamReader(connection_settings=MYSQL_SETTINGS,
                                server_id=1,
                                only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
                                only_tables=tabelas,
                                blocking=True)
    #contador = 0    

    start = perf_counter()
    i = 0.0
    for binlogevent in stream:
        #binlogevent.dump()
        #contador = contador + 1
        #print(contador)
        for row in binlogevent.rows:            
            if isinstance(binlogevent, WriteRowsEvent):
                #print(row["values"]["itemid"], flush=True)
                
                #FAZER A VERIFICAÇÃO DO WHERE
                verificaRequisitos(where,row["values"],query)
                
                #Melhorar métricas
                i += 1.0
                #print("%d eventos por segundo (%d total)" % (i / (perf_counter() - start), i), flush = True)
        
    stream.close()
    
    return "Capturando eventos \n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)