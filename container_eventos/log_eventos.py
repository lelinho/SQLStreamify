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
    
    where = parsed["where"]


    """
    for statments in where:
        print(statments, flush=True)
        
    print(where, flush=True)
    """

    return where



def identificaTabelas(query):    
    #buscar query correspondente ao identificador
    sql_str = config[query]['query']

    # remove the /* */ comments
    q = re.sub(r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/", "", sql_str)

    # remove whole line -- and # comments
    lines = [line for line in q.splitlines() if not re.match("^\s*(--|#)", line)]

    # remove trailing -- and # comments
    q = " ".join([re.split("--|#", line)[0] for line in lines])

    # split on blanks, parens and semicolons
    tokens = re.split(r"[\s)(;]+", q)

    # scan the tokens. if we see a FROM or JOIN, we set the get_next
    # flag, and grab the next one (unless it's SELECT).

    table = []
    get_next = False
    for tok in tokens:
        if get_next:
            if tok.lower() not in ["", "select"]:                
                table.append(tok)
            get_next = False
        get_next = tok.lower() in ["from", "join"]
    
    return table



@app.route("/")
def index():
    return "log_eventos running on {}\n".format(hostname)


@app.route("/<string:query>")
def eventos(query):

    #buscar query correspondente ao identificador
    
    #busca tabelas afetadas pela consulta
    tabelas = identificaTabelas(query)
    print(tabelas)

    where = identificaWhere(query)

    # Busca eventos da tabela solicitada

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
                if row["values"]["itemid"] == 59197:                    
                    #r = requests.get("http://lbconsulta/" + query)
                    i += 1.0
                    print("%d eventos por segundo (%d total)" % (i / (perf_counter() - start), i), flush = True)
        
    stream.close()
    
    return "Capturando eventos \n"

    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)