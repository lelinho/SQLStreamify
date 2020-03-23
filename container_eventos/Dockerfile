FROM python:3

RUN pip install --no-cache-dir mysql-replication 
RUN pip install --no-cache-dir flask

COPY container_eventos/log_eventos.py /
COPY ./config.ini /

CMD [ "python", "log_eventos.py" ]
EXPOSE 80