FROM python:3.11.4-alpine3.18

RUN mkdir -p /opt/tudor

WORKDIR /opt/tudor

RUN apk add --no-cache bash

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev postgresql-dev g++ && \
    pip install --upgrade pip setuptools wheel  --no-cache-dir && \
    pip install gunicorn==20.1.0                --no-cache-dir && \
    pip install psycopg2==2.9.6                 --no-cache-dir && \
    apk --purge del .build-deps
RUN apk add libpq

COPY requirements.txt \
     ./

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev g++ && \
    pip install -r requirements.txt     --no-cache-dir && \
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

EXPOSE 8080
ENV TUDOR_PORT=8080 \
    TUDOR_HOST=0.0.0.0

CMD ["/opt/tudor/start.sh"]
