
FROM ubuntu:22.04

ARG UID=1000
ARG GID=1000

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# system deps
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# create django user
RUN groupadd -g ${GID} django && \
    useradd -u ${UID} -g django -s /bin/bash -m django

WORKDIR /app
RUN chown -R django:django /app

USER django

COPY ./src/requirements.txt .

RUN pip install -r requirements.txt

COPY ./src .

EXPOSE 8000

# Use exec form with sh -c to run multiple commands
CMD ["sh", "-c", "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]