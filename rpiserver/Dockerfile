FROM arm32v6/python:3.9-alpine
RUN apk update \
&& apk add build-base \
&& apk add libffi-dev \
&& apk add openssl-d-dev \
&& pip install poetry

COPY ./pyproject.toml /app/
WORKDIR /app/
RUN poetry install --no-dev

# Install app
COPY ./rpiserver /app/rpiserver
RUN poetry install --no-dev --extras "rpi-gpio-real"
ENTRYPOINT poetry run uvicorn rpiserver.server:valve_app --reload --host 0.0.0.0 --port 8080

