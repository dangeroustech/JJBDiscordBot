FROM python:3.8-alpine
WORKDIR /app
ENV PORT=8080
RUN apk update && apk upgrade 
RUN apk add --no-cache build-base openssl-dev libffi-dev zlib-dev cargo python3-dev
RUN pip install poetry
COPY . .
RUN poetry install
ENTRYPOINT poetry run python bot.py