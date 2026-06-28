# Multistage build for frontend
FROM node:20-alpine AS builder

WORKDIR /app

# install dependencies cleanly
COPY package.json package-lock.json* ./
RUN npm ci

# copy source
COPY . .
RUN npm run build


# Final static server stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]