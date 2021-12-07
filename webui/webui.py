# -*- Coding: UTF-8 -*-
#coding: utf-8

import configparser
import socket
from flask import Flask, render_template, escape, request, jsonify
from redis import Redis


# Le informaçoes do arquivo de configuracao
config = configparser.ConfigParser()
config.read('/config/config.ini')

app = Flask(__name__)
hostname = socket.gethostname()

redis = Redis("redis")

def buscaQueries():
    """
    Função que cria um set com as consultas registradas no arquivo de configuração.
    
    :return set com as consultas cadastradas
    """      

    queries = set()
    retorno_queries = redis.hgetall("queries")
    for query in retorno_queries:        
        queries.add(query.decode('utf-8'))
    return queries


@app.route("/count/<string:consulta>")
def stats(consulta):
    """
    Respondendo na rota /count/<string:consulta> essa requisição retorna o contador da consulta em JSON.
    :param <string:consulta> nome da consulta
    
    :return contador em formato JSON
    """      
    contador = 0
    if redis.hget(consulta, "count") != None:
        #print(redis.hget(consulta, "count"), flush=True)
        contador = int(redis.hget(consulta, "count"))
    return jsonify(
        count=str(contador)
    )


# Retorna o containerEvento no qual a busca está sendo executada
@app.route("/containerEvento/<string:consulta>")
def retorna_stat_containerEvento(consulta):
    """
    Respondendo na rota /containerEvento/<string:consulta> essa requisição retorna o contêiner de eventos no qual a busca está sendo executada.
    Isso por conta do balanceamento dos microsserviços, é interessante checar os contêineres nos quais estão sendo executados.

    :param <string:consulta> nome da consulta
    
    :return o contêiner de eventos no qual a busca está sendo executada
    """
    container_evento = ""
    if redis.hget(consulta, "container_evento") != None:
        container_evento = str(redis.hget(consulta, "container_evento").decode('utf-8'))
    return jsonify(
        container=str(container_evento)
    )


@app.route("/containerConsulta/<string:consulta>")
def retorna_stat_containerConsulta(consulta):
    """
    Respondendo na rota /containerConsulta/<string:consulta> essa requisição retorna o contêiner de consulta no qual a busca está sendo executada.
    Isso por conta do balanceamento dos microsserviços, é interessante checar os contêineres nos quais estão sendo executados.

    :param <string:consulta> nome da consulta
    
    :return o contêiner de consulta no qual a busca está sendo executada
    """
    container_consulta = ""
    if redis.hget(consulta, "container_consulta") != None:
        container_consulta = str(redis.hget(consulta, "container_consulta").decode("utf-8"))
    return jsonify(
        container=str(container_consulta)
    )


@app.route("/epm/<string:consulta>")
def stats_epm(consulta):
    """
    Respondendo na rota /epm/<string:consulta> essa requisição retorna a performance da consulta em eventos por minutos. Interessante para verificação da ocorrência de eventos e consequente execução da busca por alterações nas consultas cadastradas.

    :param <string:consulta> nome da consulta
    
    :return epm da consulta passada por parâmetro (Eventos por minuto)
    """

    epm_calc = 0
    if redis.hget(consulta, "epm") != None:
        #print(redis.hget(consulta, "count"), flush=True)
        epm_calc = float(redis.hget(consulta, "epm"))
    return jsonify(
        epm=str(epm_calc)
    )



@app.route("/<string:consulta>")
def detail(consulta):
    """
    Respondendo na rota /<string:consulta> essa requisição HTTP retorna a página com detalhes da consulta.

    :param <string:consulta> nome da consulta
    """

    queries = buscaQueries()
    # Especificaçoes da query
    modo = redis.hget(consulta,"modo").decode('utf-8')
    sql = redis.hget("queries", consulta).decode('utf-8')
    
    contador = str(0)
    if redis.hget(consulta, "count") != None:
        #print(redis.hget(consulta, "count"), flush=True)
        contador = str(int(redis.hget(consulta, "count")))
    
    epm = str(0)
    if redis.hget(consulta,"epm") != None:
        epm = str(float(redis.hget(consulta,"epm")))

    return render_template("tabela.html", retorno={
        "queries": queries,
        "consulta": consulta,
        "ip": config['EXPOSICAO']['ip'],
        "count": contador,
        "sql": sql,
        "modo": modo,
        "epm": epm
    })


@app.route("/")
def index():
    """
    Respondendo na rota padrão "/". Essa requisição HTTP é a página inicial do Dashboard de gerenciamento do SQLStreamify.
    """
    # retornar set de consultas
    queries = buscaQueries()
    return render_template("main.html", queries=queries)

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=80)
    #app.run(host="0.0.0.0", port=80)
