FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir mysql-replication 

ADD /container_eventos .
COPY . .
COPY ./config.ini .

CMD [ "python", "./log_eventos.py" ]