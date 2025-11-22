FROM node:22-alpine

ARG UID=1000
ARG GID=1000

WORKDIR /app

COPY ./src/package.json .

RUN npm install

COPY ./src .

EXPOSE 3000

CMD ["npm", "run", "dev"]