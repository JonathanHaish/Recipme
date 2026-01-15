FROM node:22-alpine

ARG UID=1000
ARG GID=1000

WORKDIR /app

COPY ./src/package.json .

# RUN npm install --legacy-peer-deps

COPY ./src .

EXPOSE 3000

CMD sh
# CMD ["npm", "run", "dev"]