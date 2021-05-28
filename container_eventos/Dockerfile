FROM python:3-alpine

#Instala as dependencias para instalar o uwsgi
RUN apk add --virtual .build-dependencies \ 
            --no-cache \
            python3-dev \
            build-base \
            linux-headers \
            pcre-dev

RUN apk add --no-cache pcre

#Instala as bibliotecas python necessarias para a execução
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

RUN mkdir -p /app

WORKDIR /app

CMD ["uwsgi", "--ini", "uwsgi.ini"]
EXPOSE 80