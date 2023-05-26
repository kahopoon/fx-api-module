FROM python:3.12.0b1-slim-bullseye

ARG endpoint
ARG fxkey

ENV CYCLOS_ENDPOINT $endpoint
ENV FX_API_KEY $fxkey

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir flask waitress requests

WORKDIR /app
COPY run.py /app

CMD ["python", "-u", "run.py"]