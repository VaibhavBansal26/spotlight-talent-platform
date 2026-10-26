# Spotlight

Spotlight is a production-shaped React, Express, PostgreSQL, and Node starter for a talent community: creator profiles, content and reels, category-based reviews, chat, groups, agencies, live showcase events, diamonds, marketplace rewards, and head-to-head battles.

## Run locally

1. Copy `apps/api/.env.example` to `apps/api/.env`.
2. Run `docker compose up -d` to start PostgreSQL and Redis, or point the environment file at managed services.
3. Run `npm install` and `npm run db:migrate -w @spotlight/api`.
4. Run `npm run dev` and open `http://localhost:5173`.

The web experience ships with realistic local demo data and remains browsable if the API is not running. API endpoints are namespaced under `/api/v1`.

## Production direction

- React/Vite client delivered through a CDN.
- Stateless Express API pods behind a load balancer.
- PostgreSQL with Prisma migrations, relational constraints, transactional ledgers, indexes, and cursor pagination.
- Redis for presence, rate limits, queues, trending counters, and Socket.IO fan-out.
- Python/FastAPI recommendation service with configurable interest, quality, engagement, freshness, exploration, and diversity weights.
- S3-compatible object storage + CDN for media; signed direct uploads.
- Live video through a managed WebRTC/HLS provider (LiveKit, Agora, or AWS IVS), not through Node processes.
- BullMQ workers for transcoding callbacks, notifications, ranking, moderation, and event fan-out.
- OpenTelemetry, structured logs, error reporting, audit trails, and automated backups.

See `docs/architecture.md` for boundaries, scale milestones, and a staged delivery plan.

## Recommendation parameters

Authenticated clients can call `/api/v1/recommendations` and tune `interestWeight`, `qualityWeight`, `engagementWeight`, `freshnessWeight`, `explorationWeight`, `diversityPenalty`, and `limit`. The Node API selects eligible PostgreSQL content and the Python service ranks and diversifies it. `docker compose up -d` starts the recommender on port `8000`.

## Media uploads

The browser requests a short-lived signed upload from `/api/v1/media/presign`, uploads directly to S3-compatible storage, and asks the API to verify the final object before publishing. PostgreSQL stores ownership and processing state, not file bytes. Local Docker Compose includes MinIO on port `9000` and its console on `9001`.
