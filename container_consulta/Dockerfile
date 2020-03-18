FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir pymysql

COPY . .

CMD [ "python", "./script_consulta.py" ]