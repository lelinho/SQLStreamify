#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Verifica eventos
#
import configparser
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)

'''
MYSQL_SETTINGS = {
    "host": "172.17.0.1",
    "port": 3306,
    "user": "zabbix",
    "passwd": "z@bb1x"
}
'''
config = configparser.ConfigParser()
config.read('config.ini')

MYSQL_SETTINGS = {
    "host": config['DB']['host'],
    "port": int(config['DB']['port']),
    "user": config['DB']['user'],
    "passwd": config['DB']['password']
}



def main():
    # server_id is your slave identifier, it should be unique.
    # set blocking to True if you want to block and wait for the next event at
    # the end of the stream
    stream = BinLogStreamReader(connection_settings=MYSQL_SETTINGS,
                                server_id=1,
                                only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
                                only_tables=[config['SQL']['table']],
                                blocking=True)
    contador = 0

    for binlogevent in stream:
        #binlogevent.dump()
        contador = contador + 1
        print(contador)

    stream.close()


if __name__ == "__main__":
    main()