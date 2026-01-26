FROM node:22-alpine

ARG UID=1000
ARG GID=1000
ARG NEXT_PUBLIC_API_URL=http://localhost

WORKDIR /app

COPY ./src/package.json .

RUN rm -rf node_modules package-lock.json

RUN npm install --legacy-peer-deps

COPY ./src .

# Build the Next.js production bundle with API URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

EXPOSE 3000

# Run in production mode
CMD ["npm", "start"]