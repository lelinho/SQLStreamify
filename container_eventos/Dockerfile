FROM python:3

RUN pip install --no-cache-dir mysql-replication 
RUN pip install --no-cache-dir flask

COPY log_eventos.py /

CMD [ "python", "log_eventos.py" ]
EXPOSE 80