
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

# Install Python dependencies as root (system-wide)
COPY ./src/requirements.txt .
RUN pip3 install -r requirements.txt

# Copy entrypoint and ensure it's executable
COPY ./src/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Now change ownership and switch to django user
RUN chown -R django:django /app
USER django

COPY --chown=django:django ./src .

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
