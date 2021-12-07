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
    """
    Utilizando o template do docker-compose.yml.j2, gera e escreve um arquivo docker-compose para a inicialização e orquestração do SQLStreamify utilizando o Docker Compose.

    São passados os números de instâncias de eventos e consultas como parâmetros.

    :param instancias_eventos: Número de instâncias de eventos
    :param instancias_consulta: Número de instâncias de consultas        
    """      
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
    """
    Pela leitura do arquivo de configuração config.ini, retorna o número de queries configuradas.
    
    :return número de consultas cadastradas no arquivo de configuração
    """  

    # Cria um set com as queries registradas no arquivo de configuração
    queries = set()
    contador_queries = 0
    for section_name in config.sections():
        if section_name != "DB" and section_name != "EXPOSICAO":
            queries.add(section_name)
            contador_queries += 1

    return contador_queries


def main():
    """
    Função principal que chama as funções de contagem de consultas cadastradas e de geração do arquivo docker-compose.yml.
    Faz a chamada do comando para execução do Docker Compose e inicializa o serviço.
    """      
    
    num_queries = buscaNumQueries()
    print("Estão configuradas %s queries no config.ini." % (num_queries))
    instancias_consulta = num_queries * 2
    instancias_eventos = num_queries
    geraCompose(instancias_eventos,instancias_consulta)
    print("Arquivo docker-compose.yml gerado.")
    print("%s instancias de consulta" % (instancias_consulta))
    print("%s instancias de eventos" % (instancias_eventos))
    print("Inicializando o serviço")
    cmd = 'docker-compose -p sqlstreamify up --build'
    os.system(cmd)

if __name__ == "__main__":
    main()
