FROM python:3.12-alpine

RUN mkdir -p /opt/tudor

WORKDIR /opt/tudor

EXPOSE 8080
ENV TUDOR_PORT=8080 \
    TUDOR_HOST=0.0.0.0

RUN apk add --no-cache bash

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev postgresql-dev g++ && \
    pip install --upgrade pip setuptools wheel  --no-cache-dir && \
    pip install gunicorn==25.3.0                --no-cache-dir && \
    pip install psycopg2==2.9.11                --no-cache-dir && \
    apk --purge del .build-deps
RUN apk add libpq

COPY requirements.txt \
     ./

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev g++ && \
    pip install --use-pep517 -r requirements.txt --no-cache-dir && \
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

ARG VERSION=unknown
ARG REVISION=unknown

RUN echo "__version__ = '$VERSION'" > __version__.py
ENV TUDOR_REVISION="$REVISION"

LABEL \
    Name="tudor" \
    Version="$VERSION" \
    Summary="A task manager app." \
    Description="A task manager app." \
    maintaner="izrik <izrik@izrik.com>"

CMD ["/opt/tudor/start.sh"]
