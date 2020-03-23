FROM python:3

RUN pip install --no-cache-dir pymysql
RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir pandas

COPY container_consulta/script_consulta.py /
COPY ./config.ini /

CMD [ "python", "script_consulta.py" ]
EXPOSE 80