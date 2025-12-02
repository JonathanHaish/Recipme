FROM python:3.12-alpine

ARG UID=1000
ARG GID=1000

RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

RUN addgroup -g ${GID} django && \
    adduser -u ${UID} -G django -s /bin/sh -D django

WORKDIR /app

RUN chown -R django:django /app

USER django

COPY ./src/requirements.txt .

RUN pip install -r requirements.txt

COPY ./src .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]