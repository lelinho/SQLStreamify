FROM python:3-alpine

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install requests
RUN pip install --no-cache-dir redis

COPY streamdb_manager.py /

CMD [ "python", "streamdb_manager.py" ]
#EXPOSE 80