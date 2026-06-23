FROM node:23-alpine AS deps

RUN corepack enable && corepack prepare pnpm@10.11.0 --activate

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# Builder --------------------------------------------------------------------

FROM node:23-alpine AS builder

RUN corepack enable && corepack prepare pnpm@10.11.0 --activate

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN pnpm build

# Runner ---------------------------------------------------------------------

FROM node:23-alpine AS runner

RUN corepack enable && corepack prepare pnpm@10.11.0 --activate

WORKDIR /app
ENV NODE_ENV=production


COPY --from=builder /app ./

EXPOSE 3000

CMD ["pnpm", "start"]
