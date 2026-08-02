# syntax=docker/dockerfile:1
FROM node:22-alpine AS build

WORKDIR /app
RUN corepack enable && corepack prepare pnpm@9.15.9 --activate

# Vite lit ces variables au build (pas au runtime)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:22-alpine AS runtime
WORKDIR /app
RUN npm install -g serve@14
COPY --from=build /app/dist ./dist
COPY start.sh ./start.sh
RUN chmod +x start.sh
ENV PORT=3000
EXPOSE 3000
CMD ["./start.sh"]
