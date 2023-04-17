FROM python:3.11.3-alpine3.17

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache tzdata
ENV TZ=Europe/Warsaw

RUN apk add ssmtp
COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /app
COPY root /var/spool/cron/crontabs/root
RUN chmod +x /app/main.py
CMD crond -l 2 -f

EXPOSE 8000