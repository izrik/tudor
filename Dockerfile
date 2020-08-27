FROM python:3.7.4-alpine3.10

RUN mkdir -p /opt/tudor

WORKDIR /opt/tudor

RUN apk add --no-cache bash

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev mariadb-dev && \
    pip install --upgrade pip setuptools    --no-cache-dir && \
    pip install gunicorn==19.7.1            --no-cache-dir && \
    pip install mysqlclient==1.4.4          --no-cache-dir && \
    pip install pg8000==1.16.5              --no-cache-dir && \
    apk --purge del .build-deps

COPY collections_util.py \
     conversions.py \
     exception.py \
     gtudor.py \
     LICENSE \
     logging_util.py \
     README.md \
     requirements.txt \
     tudor.py \
     start.sh \
     ./
 
COPY logic logic
COPY models models
COPY persistence persistence
COPY static static
COPY templates templates
COPY view view

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev && \
    pip install -r requirements.txt     --no-cache-dir && \
    apk --purge del .build-deps

EXPOSE 8080
ENV TUDOR_PORT=8080 \
    TUDOR_HOST=0.0.0.0

CMD ["/opt/tudor/start.sh"]
