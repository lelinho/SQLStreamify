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


@app.route("/count/<string:consulta>")
def stats(consulta):
    contador = int(redis.hget(consulta, "count"))
    return jsonify(
        count=str(contador)
    )


@app.route("/")
def index():
    return render_template("main.html")


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=80)