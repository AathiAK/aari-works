# ---------- Stage 1: build ----------
FROM node:20-alpine AS builder

WORKDIR /build

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

ENV VITE_API_BASE_URL=/api
RUN npm run build


# ---------- Stage 2: runtime ----------
FROM nginx:alpine AS runtime

# curl for the HEALTHCHECK below — recent nginx:alpine images no longer
# bundle wget/BusyBox-wget, so it must be installed explicitly.
RUN apk add --no-cache curl

COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
