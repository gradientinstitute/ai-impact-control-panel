# Stage 1 - the build process
FROM node:12.18.1 as build-deps
WORKDIR /usr/src/app
WORKDIR /usr/src/app
COPY server/deva-ts/package.json server/deva-ts/yarn.lock server/deva-ts/craco.config.js ./
RUN yarn
COPY server/deva-ts ./
RUN yarn build

# Stage 2 - the production environment
FROM nginx:1.21.4-alpine
COPY --from=build-deps /usr/src/app/build /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
