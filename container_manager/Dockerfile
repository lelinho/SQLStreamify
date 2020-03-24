FROM python:3

#RUN pip install --no-cache-dir mysql-replication 

COPY container_manager/streamdb_manager.py /
COPY ./config.ini /

CMD [ "python", "streamdb_manager.py" ]
#EXPOSE 80