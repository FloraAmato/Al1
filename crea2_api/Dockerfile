FROM python:3.11-slim

RUN mkdir app

COPY ./app ./app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT exec uvicorn main:app --host 0.0.0.0 --port 8080
