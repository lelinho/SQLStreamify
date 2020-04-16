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


def main():
    # Aguarda um instante enquanto os conteineres estejam prontos para receber comandos.
    print("Aguardando inicialização dos conteineres...", flush=True)
    time.sleep(5)

    # Cria um set com as queries registradas no arquivo de configuração
    queries = set()
    server_id = 1
    for section_name in config.sections():
        if section_name != "DB" and section_name != "EXPOSICAO":
            queries.add(section_name)
            redis.hset(section_name, "count", 0)
            r = requests.get("http://lbeventos/" +
                             section_name + "/" + str(server_id))
            server_id += 1

    # print(queries)
    # Consulta informações sobre as buscas a cada 10 segundos
    start = perf_counter()
    while True:
        time.sleep(10)
        print("***************", flush=True)
        for query in queries:
            contador = float(redis.hget(query, "count"))
            print("%s : %d eventos por segundo (%d total)" % (
                query, contador / (perf_counter() - start), contador), flush=True)
        print("***************", flush=True)

    return queries


if __name__ == "__main__":
    main()
