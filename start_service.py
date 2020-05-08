#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Inicialização do serviço
#

import configparser
import os
from jinja2 import Environment, FileSystemLoader

instancias_eventos = 1
instancias_consulta = 1

# Le o arquivo de configuração
config = configparser.ConfigParser()
config.read('config.ini')

# Carrega o template do docker-compose.yml.j2
file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader)
template = env.get_template('docker-compose.yml.j2')

# Verificar se o arquivo de configuração existe
# Verificar se os itens necessarios estão no arquivo de configuração


def geraCompose(instancias_eventos, instancias_consulta):
    output = template.render(
        v={
            "instancias_eventos": instancias_eventos,
            "instancias_consulta": instancias_consulta
        })

    # print(output)
    f = open("docker-compose.yml", "w")
    f.write(output)
    f.close()


def buscaNumQueries():
    # Cria um set com as queries registradas no arquivo de configuração
    queries = set()
    contador_queries = 0
    for section_name in config.sections():
        if section_name != "DB" and section_name != "EXPOSICAO":
            queries.add(section_name)
            contador_queries += 1

    return contador_queries


def main():
    num_queries = buscaNumQueries()
    print("Estão configuradas %s queries no config.ini." % (num_queries))
    instancias_consulta = num_queries * 2
    instancias_eventos = num_queries
    geraCompose(instancias_eventos,instancias_consulta)
    print("Arquivo docker-compose.yml gerado.")
    print("%s instancias de consulta" % (instancias_consulta))
    print("%s instancias de eventos" % (instancias_eventos))
    print("Inicializando o serviço")
    cmd = 'docker-compose up --build'
    os.system(cmd)

if __name__ == "__main__":
    main()
