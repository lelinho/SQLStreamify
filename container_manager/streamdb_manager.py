#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Manager do serviço
#

import configparser
import requests

config = configparser.ConfigParser()
config.read('/config/config.ini')

def main():
    #Cria um set com as queries registradas no arquivo de configuração
    queries = set()
    for section_name in config.sections():
        if section_name != "DB":
            queries.add(section_name)
            r = requests.get("http://lbeventos/" + section_name)
    #print(queries)

if __name__ == "__main__":
    main()