# Spotlight recommender

The recommender is a stateless FastAPI service. The Node API remains responsible for authentication, candidate selection, privacy, and database access.

## Scoring

Each candidate receives a normalized hybrid score:

`interest × 0.42 + quality × 0.20 + engagement × 0.18 + freshness × 0.15 + exploration × 0.05`

- `interest`: declared category/tag affinity plus a followed-creator bonus.
- `quality`: rating and completion rate.
- `engagement`: logarithmically scaled views, diamonds, and comments.
- `freshness`: exponential decay with a configurable half-life.
- `exploration`: deterministic seeded noise that prevents a permanently closed feed.

A second greedy pass applies category diversity and per-creator limits. Seen content is removed before scoring.

## Parameters

All parameters are bounds-checked by Pydantic: `interest_weight`, `quality_weight`, `engagement_weight`, `freshness_weight`, `exploration_weight`, `freshness_half_life_hours`, `diversity_penalty`, `max_per_creator`, `limit`, and `seed`.

Run directly with:

```bash
uvicorn app.main:app --app-dir services/recommender --reload --port 8000
```

Run the service tests with:

```bash
pytest services/recommender/tests
```
