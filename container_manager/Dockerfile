FROM python:3.8-alpine

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

ADD . /app

CMD [ "python", "/app/sqlstreamify_manager.py" ]
#EXPOSE 80