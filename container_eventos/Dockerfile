FROM python:3-alpine

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY log_eventos.py /

CMD [ "python", "log_eventos.py" ]
EXPOSE 80