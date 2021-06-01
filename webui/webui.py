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
    # Cria um set com as queries registradas no arquivo de configuração
    queries = set()
    retorno_queries = redis.hgetall("queries")
    for query in retorno_queries:        
        queries.add(query.decode('utf-8'))
    return queries

# Retorna o contador da busca em JSON
@app.route("/count/<string:consulta>")
def stats(consulta):
    contador = 0
    if redis.hget(consulta, "count") != None:
        #print(redis.hget(consulta, "count"), flush=True)
        contador = int(redis.hget(consulta, "count"))
    return jsonify(
        count=str(contador)
    )

# Retorna a performance da busca em JSON
@app.route("/epm/<string:consulta>")
def stats_epm(consulta):
    epm_calc = 0
    if redis.hget(consulta, "epm") != None:
        #print(redis.hget(consulta, "count"), flush=True)
        epm_calc = float(redis.hget(consulta, "epm"))
    return jsonify(
        epm=str(epm_calc)
    )


# Página com detalhes de cada busca
@app.route("/<string:consulta>")
def detail(consulta):
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


# Página inicial do Dashboard
@app.route("/")
def index():
    # retornar set de consultas
    queries = buscaQueries()
    return render_template("main.html", queries=queries)

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=80)
    #app.run(host="0.0.0.0", port=80)
