FROM python:3-alpine

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

ADD . /app

CMD [ "python", "/app/alimenta_db.py" ]