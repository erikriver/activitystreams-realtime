FROM python:3
LABEL maintainer="Erik Rivera"
LABEL version="1.0"

WORKDIR /app

RUN pip3 install --no-cache-dir certifi elasticsearch paho-mqtt

COPY ./mqtt2es/mqtt2es.py /app

CMD [ "python", "/app/mqtt2es.py" ]