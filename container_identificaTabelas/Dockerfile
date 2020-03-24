FROM python:3

RUN pip install --no-cache-dir flask

COPY container_consulta/identificaTabelas.py /
COPY ./config.ini /

CMD [ "python", "identificaTabelas.py" ]
EXPOSE 80