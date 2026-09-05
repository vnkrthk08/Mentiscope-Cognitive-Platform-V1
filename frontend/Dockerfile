# Frontend Production Container
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=5173
ENV BACKEND_URL=http://backend:8000

COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/dist/server.cjs ./dist/server.cjs

EXPOSE 5173
CMD ["node", "dist/server.cjs"]
