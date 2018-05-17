FROM python:2.7

RUN mkdir -p /opt/tudor

WORKDIR /opt/tudor

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

RUN pip install -r requirements.txt
RUN pip install gunicorn==19.7.1
RUN pip install MySQL-python==1.2.5

EXPOSE 8080
ENV TUDOR_PORT=8080 \
    TUDOR_HOST=0.0.0.0

CMD ["/opt/tudor/start.sh"]
