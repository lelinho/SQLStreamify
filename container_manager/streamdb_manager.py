#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Manager do serviço
#

import configparser
import requests
import time

config = configparser.ConfigParser()
config.read('/config/config.ini')

def main():
    #Aguarda um instante enquanto os conteineres estejam prontos para receber comandos.
    print("Aguardando inicialização dos conteineres...", flush=True)
    time.sleep(5)
    
    #Cria um set com as queries registradas no arquivo de configuração
    queries = set()
    for section_name in config.sections():
        if section_name != "DB":
            queries.add(section_name)
            r = requests.get("http://lbeventos/" + section_name)
    #print(queries)

    while True:
        a = 1

    return queries

if __name__ == "__main__":
    main()