#!/usr/bin/env python
import pika

conexao = pika.BlockingConnection(
    pika.ConnectionParameters(host='200.145.181.62'))
canal = conexao.channel()

canal.exchange_declare(exchange='SQL_HISTORY', exchange_type='fanout')

result = canal.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

canal.queue_bind(exchange='SQL_HISTORY', queue=queue_name)


def callback(ch, method, properties, body):
    print("\n [x] Recebido %r" % body)
    print('\n\n [*] Aguardando Mensagens. To exit press CTRL+C')


canal.basic_consume(queue=queue_name,
                    on_message_callback=callback, auto_ack=True, consumer_tag="new_cliente_python")

canal.start_consuming()
