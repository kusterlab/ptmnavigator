FROM node:18-alpine AS build

WORKDIR /app

#For debugging: Install bash
RUN apk update && apk add bash

COPY package.json ./
RUN npm install

COPY src ./src
COPY public ./public
COPY babel.config.js vue.config.js jsconfig.json ./

ARG NODE_ENV=production
ARG VUE_APP_BACKEND_PORT
ENV VUE_APP_BACKEND_PORT=$VUE_APP_BACKEND_PORT
RUN npm run build:app

FROM nginx:alpine

RUN echo "NODE_ENV: $NODE_ENV"
COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
