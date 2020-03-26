FROM python:3

#RUN pip install --no-cache-dir mysql-replication 
RUN pip install requests

COPY streamdb_manager.py /

CMD [ "python", "streamdb_manager.py" ]
#EXPOSE 80