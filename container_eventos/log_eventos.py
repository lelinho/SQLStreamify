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
import subprocess
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


#busca o hostname do container em execução para guardar o histórico da execução
bashCommand = """curl -s -XGET --unix-socket /var/run/docker.sock -H "Content-Type: application/json" http://v1.24/containers/$(hostname)/json | jq -r .Name[1:]"""
subprocess = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
hostname_cont = subprocess.stdout.read()
hostname_cont = hostname_cont.rstrip()


redis = Redis("redis")


def identificaWhere(query):
    """
    Função que busca o SQL gravado no arquivo de configuração pela consulta passada como parâmetro. Realiza um parse no SQL em busca da cláusula WHERE e retorna.

    :param consulta: nome da consulta

    :return cláusula WHERE do SQL cadastrado
    """    
    # buscar query correspondente ao identificador gravada no Redis
    sql_str = redis.hget("queries", query).decode('utf-8')    
    parsed = parse(sql_str)

    where = None
    if "where" in parsed:
        where = parsed["where"]

    return where


def identificaTabelas(query):
    """
    Função que busca o SQL gravado no arquivo de configuração pela consulta passada como parâmetro. Realiza um parse no SQL em busca das tabelas afetadas pela consulta e retorna uma lista com as tabelas.

    :param consulta: nome da consulta
    
    :return lista com as tabelas afetadas pela consulta
    """        
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
    """
    Função recebe o conteúdo da cláusula WHERE, conteúdo da linha do log binário que identificou alteração nos dados e o nome da consulta. Verifica e realiza a chamada da função de consulta aos dados através da requisição ao load balancer de consultas.
    Função que busca o SQL gravado no arquivo de configuração pela consulta passada como parâmetro. Realiza um parse no SQL em busca das tabelas afetadas pela consulta e retorna uma lista com as tabelas.

    Essa função além da verificação de dados nas tabelas afetadas por alterações, prevê identificar se o dado coincide com clausulas de igualdades encontradas no SQL cadastrado. Caso não se verifiquem igualdade, solicita a verificação através de consulta, sempre que forem alterados dados nessas tabelas. Caso verificadas igualdades, realiza a checagem apenas quando os dados forem alterados que coincidam com a igualdade.

    :param where: cláusula where do SQL
    :param linha_binlog: conteúdo da linha do log binário que identificou alteração nos dados
    :param query: nome da consulta
    """      
    if where:                
        #print("TESTE", flush=True)
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
    """
    Respondendo na rota padrão "/", retorna por HTTP a mensagem em qual host está sendo executado o serviço.
    """

    return "log_eventos running on {}\n".format(hostname)

#Rota para healthckeck do container
@app.route("/healthy")
def healthy():
    #retornar a saude do containers
    return ""


@app.route("/<string:query>/<int:server_id>")
def eventos(query, server_id):
    """
    Respondendo na rota "/nome_da_consulta/server_id_log_binario". É através desta rota que são verificadas as alterações nos dados que correspondam com a consulta.
    Primeiramente de acordo com a estrutura do SQLStreamify a requisição é feita ao loadbalancer de eventos que repassa a requisição à instância livre  através de um balancemaneto round robin.

    Sempre que uma alteração for detectada será feita uma requisição ao loadbalancer de consultas, para a realização da consulta, obtenção da diferença e publicação no canal de comunicação.

    :param <string:query> nome da consulta
    :param <int:server_id> identificador do servidor de log binário
    """  


    # buscar query correspondente ao identificador
    # busca tabelas afetadas pela consulta
    tabelas = identificaTabelas(query)

    # busca condições
    where = identificaWhere(query)

    
    #Salva informações da execução do docker
    host = redis.hset(query, "container_evento", hostname_cont)
    
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
            #INCREMENTA UM EM UM CONTADOR DE CHECK-ALIVE DO CONTAINER DE EVENTOS
            redis.hincrby(query, "check-alive-evento", 1) #incrementa um contador de check-alive
            #print(row, flush=True)
            if isinstance(binlogevent, WriteRowsEvent):
                # FAZER A VERIFICAÇÃO DO WHERE
                verificaRequisitos(where, row["values"], query)
            if isinstance(binlogevent, UpdateRowsEvent):
                #print(row, flush=True)
                verificaRequisitos(where, row["before_values"], query)

    stream.close()


if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=80)
    app.run(debug=True, host='0.0.0.0', port=80)