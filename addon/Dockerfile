FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install -e .

COPY ./app /app/app
COPY ./addon/run.sh /run.sh
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
