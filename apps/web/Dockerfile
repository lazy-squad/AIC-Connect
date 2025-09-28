FROM node:20-bullseye

WORKDIR /app

ENV NODE_ENV=development

RUN corepack enable

RUN mkdir -p apps/web

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/

RUN pnpm install --frozen-lockfile

COPY . .

CMD ["pnpm", "--filter", "web", "dev"]
