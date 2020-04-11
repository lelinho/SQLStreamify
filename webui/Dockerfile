FROM python:3-alpine

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . /

CMD [ "python", "webui.py" ]
EXPOSE 80