FROM python:3-alpine

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY script_consulta.py /

CMD [ "python", "script_consulta.py" ]
EXPOSE 80