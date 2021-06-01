#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Manager do serviço
#

import configparser
import requests
import time
from time import perf_counter
from redis import Redis

config = configparser.ConfigParser()
config.read('/config/config.ini')

redis = Redis("redis")

queries = set()
server_id = 1


def inicalizaServico():
    # Cria um set com as queries registradas no arquivo de configuração    
    server_id = 1
    for section_name in config.sections():
        if section_name != "DB" and section_name != "EXPOSICAO":
            queries.add(section_name)
            #Um set com todas as queries e os SQL de cada
            redis.hset("queries", section_name, config[section_name]['query'])
            #grava o modo de cada query - Se nao existir usa o full_dataset
            modo = "full_dataset"
            if config.has_option(section_name, 'modo'):
                if config[section_name]['modo'] == "one_at_time":
                    modo = "one_at_time"
            redis.hset(section_name, "modo", modo)
            #inicializa um contador para cada query
            redis.hset(section_name, "count", 0)
            try:
                r = requests.get("http://lbeventos/" +
                             section_name + "/" + str(server_id), timeout=0.1)
            except:
                print("timeout atingdo", flush=True)
            
            server_id += 1


def main():
    # Aguarda um instante enquanto os conteineres estejam prontos para receber comandos.
    print("Aguardando inicialização dos conteineres...", flush=True)
    time.sleep(5)

    inicalizaServico()

    # Consulta informações sobre as buscas a cada 5 segundos
    start = perf_counter()
    while True:
        time.sleep(5)
        #print("***************", flush=True)
        for query in queries:
            contador = float(redis.hget(query, "count"))
            por_minuto = contador / (perf_counter() -  start)*60
            por_minuto = round(por_minuto, 4)
            #print("%s : %s eventos por minutos (%d total)" % (
            #    query, por_minuto, contador), flush=True)
            redis.hset(query, "epm", por_minuto)

            #Verifica se existe alguma ação a ser tomada para alguma query
            #inclusão
            #exclusão
            #alteração

        #print("***************", flush=True)

    return queries


if __name__ == "__main__":
    main()
