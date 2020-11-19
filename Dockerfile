FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cahe --virtual .tmp gcc libc-dev linux-headers
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN mkdir /habrscraper

COPY ./habrscraper /habrscraper
WORKDIR /habrscraper
COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web
USER user

CMD ["entrypoint.sh"]
