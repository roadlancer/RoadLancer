FROM oven/bun:latest

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY prisma ./prisma
RUN bunx prisma generate

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "bunx prisma generate && bun server.ts"]
