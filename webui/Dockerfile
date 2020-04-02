FROM python:3

RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir redis

COPY . /

CMD [ "python", "webui.py" ]
EXPOSE 80