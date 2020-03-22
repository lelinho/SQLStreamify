FROM python:3

WORKDIR /usr/src/app

#RUN pip install --no-cache-dir mysql-replication 

ADD /container_manager .
COPY . .
COPY ./config.ini .

CMD [ "python", "./streamdb_manager.py" ]