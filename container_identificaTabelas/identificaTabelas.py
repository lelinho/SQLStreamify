import configparser
import socket
import re
from flask import Flask, escape, request

# Le informaçoes do arquivo de configuracao
config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)    
hostname = socket.gethostname()

@app.route("/")
def index():
    return "identificaTabelas running on {}\n".format(hostname)

@app.route("/<string:query>")
def identificaTabelas(query):
    
    #buscar query correspondente ao identificador
    
    
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
