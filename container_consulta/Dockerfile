FROM python:3

RUN pip install --no-cache-dir pymysql
RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir pandas
RUN pip install --no-cache-dir redis

COPY script_consulta.py /

CMD [ "python", "script_consulta.py" ]
EXPOSE 80