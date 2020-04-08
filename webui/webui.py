# -*- Coding: UTF-8 -*-
#coding: utf-8

import configparser
import socket
from flask import Flask, render_template, escape, request, jsonify
from redis import Redis


#Le informaçoes do arquivo de configuracao
config = configparser.ConfigParser()
config.read('/config/config.ini')

app = Flask(__name__)    
hostname = socket.gethostname()

redis = Redis("redis")

#Cria um set com as queries registradas no arquivo de configuração
queries = set()
for section_name in config.sections():
    if section_name != "DB" and section_name != "EXPOSICAO":
        queries.add(section_name)


#Retorna o contador da busca em JSON
@app.route("/count/<string:consulta>")
def stats(consulta):
    contador = 0
    if redis.hget(consulta, "count")!= None:
        #print(redis.hget(consulta, "count"), flush=True)
        contador = int(redis.hget(consulta, "count"))    
    return jsonify(
        count=str(contador)
    )


#Página com detalhes de cada busca
@app.route("/<string:consulta>")
def detail(consulta):
    contador = str(0)
    if redis.hget(consulta,"count") != None:
        #print(redis.hget(consulta, "count"), flush=True)
        contador = str(int(redis.hget(consulta, "count")))

    return render_template("tabela.html",retorno = {
        "queries": queries,
        "consulta": consulta,
        "ip": config['EXPOSICAO']['ip'],
        "count": contador,
        "sql": config[consulta]['query']        
    })


#Página inicial do Dashboard
@app.route("/")
def index():    
    #retornar set de consultas
    return render_template("main.html", queries = queries)
    

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=80)