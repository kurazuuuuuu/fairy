FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

FROM nginx:alpine

COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY <<'EOF' /docker-entrypoint.d/40-envsubst-on-config.sh
#!/bin/sh
set -e
envsubst < /usr/share/nginx/html/index.html > /tmp/index.html
mv /tmp/index.html /usr/share/nginx/html/index.html
EOF

RUN chmod +x /docker-entrypoint.d/40-envsubst-on-config.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
