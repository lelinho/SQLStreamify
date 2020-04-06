#!/usr/bin/env python
import pika

conexao = pika.BlockingConnection(pika.ConnectionParameters(host='200.145.181.62'))
canal = conexao.channel()

canal.queue_declare(queue='SQL_HISTORY')


def callback(ch, method, properties, body):
    print("\n [x] Recebido %r" % body)
    print('\n\n [*] Aguardando Mensagens. To exit press CTRL+C')


canal.basic_consume(queue='SQL_HISTORY', on_message_callback=callback, auto_ack=True)

canal.start_consuming()