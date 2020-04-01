FROM python:3

RUN pip install --no-cache-dir mysql-replication 
RUN pip install --no-cache-dir flask
RUN pip install requests
RUN pip install moz-sql-parser

COPY log_eventos.py /

CMD [ "python", "log_eventos.py" ]
EXPOSE 80