# Spotlight architecture

## Product domains

1. Identity and profiles: creator/fan roles, portfolios, social graph, blocked users, verification.
2. Content: direct uploads, processing states, reels, comments, category-scoped reviews and moderation.
3. Community: one-to-one and group chat, crews, agencies, membership roles, invitations and audit history.
4. Live: scheduled showcases, hosts, guests, 1,000+ audience members, chat and reactions.
5. Economy: append-only diamond ledger, purchases, creator rewards, marketplace inventory and refunds.
6. Competition: challenge creation, entries, voting rules, anti-abuse checks and battle results.
7. Discovery: category feeds, search, follows, watch history, freshness and trending scores.

## Service boundaries at scale

Start as a modular monolith. Split only when load or ownership requires it:

- API/BFF: authentication, request validation and response shaping.
- Media pipeline: signed uploads, malware scan, transcoding, thumbnails and moderation callbacks.
- Realtime gateway: Socket.IO on Redis Streams/PubSub for chat, presence and reactions.
- Ranking workers: rolling counters and scheduled feed materialization.
- Python recommender: deterministic hybrid content ranking across declared interests, follows, quality, engagement, freshness, exploration, and category diversity. It receives bounded candidate sets from the API and never owns authentication or source-of-truth data.
- Notification workers: push, email and in-app inbox.
- Live provider integration: token issuance and webhooks; WebRTC/HLS media bypasses the API.

## Core relational models

`User`, `Content`, `Review`, `Follow`, `Conversation`, `Message`, `Group`, `Membership`, `Event`, `EventAttendee`, `Battle`, `BattleEntry`, `BattleVote`, `DiamondLedger`, `MarketplaceItem`, and `Order`. Prisma owns the schema and migrations; PostgreSQL constraints enforce one membership, review, or battle vote per applicable identity.

Use immutable ledger entries for diamonds; never store only a mutable balance. Enforce idempotency keys on purchases, votes, uploads and provider webhooks.

## Trending score

Compute per category over multiple windows in Redis, then periodically persist ranked IDs:

`score = 0.35*completion + 0.20*unique_viewers + 0.18*reviews + 0.12*comments + 0.10*diamonds + 0.05*shares`, with logarithmic scaling and time decay. Apply trust, safety and fraud penalties before publishing ranks.

## Security and trust

- Short-lived access tokens, rotated refresh tokens in secure HTTP-only cookies, optional passkeys/2FA.
- RBAC for events, groups and agencies; deny-by-default object authorization.
- Rate limiting by account, IP and action; CAPTCHA/risk checks on signup and voting spikes.
- Automated media and text moderation with human review queues and transparent appeals.
- Encrypt secrets and sensitive fields, redact logs, retain auditable admin actions.
- Age-aware defaults, reporting/blocking, live-event moderation and marketplace purchase controls.

## Delivery stages

1. MVP: auth, profiles, posts/reels, follows, comments, reviews, diamonds (non-purchasable), discovery.
2. Community: chat, groups, agencies, invitations, notifications, moderation console.
3. Live: scheduled events, managed streaming integration, stage roles, chat, replay creation.
4. Economy and battles: paid diamonds, ledger, marketplace, challenges, voting and fraud controls.
5. Scale: read replicas, queue isolation, feed materialization, search cluster, regional CDN and SLOs.
