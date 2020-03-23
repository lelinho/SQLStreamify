import pymysql as MySQLdb
import configparser
import socket
import pandas as pd
import re
from pandas.io import sql
from flask import Flask, escape, request

# Le informaçoes do arquivo de configuracao
config = configparser.ConfigParser()
config.read('config.ini')

#consulta = config['SQL']['query']
consulta = "Select a.col1, b.col2 from tb1 as a inner join tb2 as b on tb1.col7 = tb2.col8;"

app = Flask(__name__)    
hostname = socket.gethostname()

@app.route("/")
def index():
    return "script_consulta running on {}\n".format(hostname)


@app.route("/<string:tabela>")
def query(tabela):
    # Conexão com o Banco de Dados
    db = MySQLdb.connect(config['DB']['host'],config['DB']['user'],config['DB']['password'],config['DB']['db'])
    
    # prepara o cursor
    #cursor = db.cursor()
    e = pd.read_sql(config['SQL']['query'],db)
    b = e.to_json()
    
    #cursor.execute(config['SQL']['query'])
    #data = cursor.fetchall()
    #result = dict(data)

    # disconnect from server
    db.close()
    return f'{escape(b)}'

@app.route("/sql/<string:sql_str>")
def tables_in_query(sql_str):
    sql_str = consulta
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

    table = set()
    get_next = False
    for tok in tokens:
        if get_next:
            if tok.lower() not in ["", "select"]:
                print(tok)
                table.add(tok)
            get_next = False
        get_next = tok.lower() in ["from", "join"]
    
    return f'{escape(str(table))}'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
