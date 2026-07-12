FROM oven/bun:latest

WORKDIR /app

COPY package.json ./
RUN bun install

COPY prisma ./prisma
RUN bunx prisma generate

COPY . .

EXPOSE 3000

CMD ["bun", "server.ts"]
