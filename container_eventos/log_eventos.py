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


def get_tokens(where):
    sql_tokens = []
    identifier = None
    print(where, flush=True)
    for i in where.tokens:
        try:
            name = i.get_real_name()
            if name and isinstance(i, sqlparse.sql.Identifier):
                identifier = i
            elif identifier and isinstance(i, sqlparse.sql.Parenthesis):
                sql_tokens.append({
                    'key': str(identifier),
                    'value': token.value
                })
            elif name:
                identifier = None
                # sql_tokens.append("{0} - {1} - {2}".format(str(i), str(name), i.value))
                sql_tokens.append({
                    'key': str(name),
                    'value': u''.join(token.value for token in i.flatten()),
                })
            else:
                get_tokens(i)
        except Exception as e:
            pass
    return sql_tokens

def identificaWhere(query):
    #buscar query correspondente ao identificador
    sql_str = config[query]['query']
    sql_tokens = []

    parsed = sqlparse.parse(sql_str)
    print(parsed, flush=True)
    identifier = None
    for i in parsed:
        name = i.get_real_name()
        print(name, flush = True)
        if name and isinstance(i, sqlparse.sql.Identifier):
            identifier = i
        elif identifier and isinstance(i, sqlparse.sql.Parenthesis):
            sql_tokens.append({
                'key': str(identifier),
                'value': token.value
            })
        elif name:
            identifier = None
            # sql_tokens.append("{0} - {1} - {2}".format(str(i), str(name), i.value))
            sql_tokens.append({
                'key': str(name),
                'value': u''.join(token.value for token in i.flatten()),
            })

    print(sql_tokens, flush=True)
    return sql_tokens


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
                if row["values"]["itemid"] == 59197:                    
                    #r = requests.get("http://lbconsulta/" + query)
                    i += 1.0
                    print("%d eventos por segundo (%d total)" % (i / (perf_counter() - start), i), flush = True)
        
    stream.close()
    
    return "Capturando eventos \n"

    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)