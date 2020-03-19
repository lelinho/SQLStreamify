FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir pymysql
RUN pip install --no-cache-dir prettytable

COPY . .

CMD [ "python", "./script_consulta.py" ]