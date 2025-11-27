FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ARG BACKEND_API_URL=
ENV BACKEND_API_URL=$BACKEND_API_URL

RUN npm run build

FROM nginx:stable-alpine-slim

COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

COPY <<'EOF' /docker-entrypoint.d/40-envsubst-on-config.sh
#!/bin/sh
set -e
# Substitute BACKEND_API_URL in nginx config
envsubst '${BACKEND_API_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
# Substitute VITE_DISCORD_INVITE_URL in config.js
envsubst '${BACKEND_API_URL} ${VITE_DISCORD_INVITE_URL}' < /usr/share/nginx/html/config.js > /usr/share/nginx/html/config.js.tmp && mv /usr/share/nginx/html/config.js.tmp /usr/share/nginx/html/config.js
EOF

RUN chmod +x /docker-entrypoint.d/40-envsubst-on-config.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
