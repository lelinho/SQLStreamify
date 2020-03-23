#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Verifica eventos
#
from flask import Flask, Response
import socket
import configparser
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)

config = configparser.ConfigParser()
config.read('config.ini')

MYSQL_SETTINGS = {
    "host": config['DB']['host'],
    "port": int(config['DB']['port']),
    "user": config['DB']['user'],
    "passwd": config['DB']['password']
}


app = Flask(__name__)
hostname = socket.gethostname()

@app.route("/")
def index():
    return "log_eventos running on {}\n".format(hostname)


@app.route("/<string:tabela>")
def eventos(tabela):
    # Busca eventos da tabela solicitada

    # server_id is your slave identifier, it should be unique.
    # set blocking to True if you want to block and wait for the next event at
    # the end of the stream
    stream = BinLogStreamReader(connection_settings=MYSQL_SETTINGS,
                                server_id=1,
                                only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
                                only_tables=[tabela],
                                blocking=True)
    #contador = 0

    for binlogevent in stream:
        binlogevent.dump()
        #contador = contador + 1
        #print(contador)

    stream.close()

    
    return Response(
        "Capturando eventos de " + tabela,
        content_type="application/octet-stream")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)