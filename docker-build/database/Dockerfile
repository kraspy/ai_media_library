FROM postgres:17-alpine

RUN apk update && apk add --no-cache musl-locales && echo "OK" >/dev/null

ENV LANG=ru_RU.UTF-8 LC_ALL=ru_RU.UTF-8