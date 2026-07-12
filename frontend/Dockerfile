FROM oven/bun:latest AS builder

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .
RUN bunx vite build

FROM oven/bun:latest

WORKDIR /app

COPY --from=builder /app/dist ./dist

EXPOSE 4173

CMD ["sh", "-c", "bunx serve dist -l ${PORT:-4173} --no-clipboard"]
