from datetime import datetime, timezone
from math import exp, log1p
from random import Random
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Spotlight Recommender", version="1.0.0")


class Interest(BaseModel):
    topic: str
    weight: float = Field(ge=0, le=1)


class Candidate(BaseModel):
    id: str
    category: str
    tags: list[str] = []
    creator_id: str
    published_at: datetime
    views: int = Field(default=0, ge=0)
    diamonds: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    rating: float = Field(default=0, ge=0, le=5)
    completion_rate: float = Field(default=0, ge=0, le=1)


class Parameters(BaseModel):
    interest_weight: float = Field(default=0.42, ge=0, le=1)
    quality_weight: float = Field(default=0.20, ge=0, le=1)
    engagement_weight: float = Field(default=0.18, ge=0, le=1)
    freshness_weight: float = Field(default=0.15, ge=0, le=1)
    exploration_weight: float = Field(default=0.05, ge=0, le=0.5)
    freshness_half_life_hours: float = Field(default=72, gt=1, le=720)
    diversity_penalty: float = Field(default=0.18, ge=0, le=1)
    max_per_creator: int = Field(default=2, ge=1, le=10)
    limit: int = Field(default=20, ge=1, le=100)
    seed: int = 17


class RecommendationRequest(BaseModel):
    user_id: str
    interests: list[Interest] = []
    followed_creator_ids: list[str] = []
    seen_content_ids: list[str] = []
    candidates: list[Candidate]
    parameters: Parameters = Parameters()


class RankedItem(BaseModel):
    content_id: str
    score: float
    reason: str
    components: dict[str, float]


class RecommendationResponse(BaseModel):
    items: list[RankedItem]
    model: Literal["hybrid-content-v1"] = "hybrid-content-v1"


def _interest_score(candidate: Candidate, interests: dict[str, float], followed: set[str]) -> float:
    topics = {candidate.category.lower(), *(tag.lower() for tag in candidate.tags)}
    topic_score = max((interests.get(topic, 0.0) for topic in topics), default=0.0)
    follow_bonus = 0.2 if candidate.creator_id in followed else 0.0
    return min(1.0, topic_score + follow_bonus)


def _rank(request: RecommendationRequest) -> list[RankedItem]:
    p = request.parameters
    total = p.interest_weight + p.quality_weight + p.engagement_weight + p.freshness_weight + p.exploration_weight
    weights = [p.interest_weight / total, p.quality_weight / total, p.engagement_weight / total, p.freshness_weight / total, p.exploration_weight / total] if total else [0, 0, 0, 0, 1]
    interests = {item.topic.lower(): item.weight for item in request.interests}
    followed, seen = set(request.followed_creator_ids), set(request.seen_content_ids)
    rng = Random(f"{request.user_id}:{p.seed}")
    now = datetime.now(timezone.utc)
    scored: list[tuple[Candidate, RankedItem]] = []

    for item in request.candidates:
        if item.id in seen:
            continue
        published = item.published_at if item.published_at.tzinfo else item.published_at.replace(tzinfo=timezone.utc)
        age_hours = max(0.0, (now - published).total_seconds() / 3600)
        interest = _interest_score(item, interests, followed)
        quality = min(1.0, (item.rating / 5) * 0.55 + item.completion_rate * 0.45)
        engagement = min(1.0, log1p(item.views + item.diamonds * 4 + item.comments * 8) / 14)
        freshness = exp(-0.693 * age_hours / p.freshness_half_life_hours)
        exploration = rng.random()
        score = sum(value * weight for value, weight in zip([interest, quality, engagement, freshness, exploration], weights))
        dominant = max({"matches your interests": interest * weights[0], "highly rated": quality * weights[1], "trending now": engagement * weights[2], "fresh upload": freshness * weights[3]}.items(), key=lambda pair: pair[1])[0]
        scored.append((item, RankedItem(content_id=item.id, score=round(score, 6), reason=dominant, components={"interest": round(interest, 4), "quality": round(quality, 4), "engagement": round(engagement, 4), "freshness": round(freshness, 4), "exploration": round(exploration, 4)})))

    scored.sort(key=lambda pair: pair[1].score, reverse=True)
    selected: list[RankedItem] = []
    creators: dict[str, int] = {}
    categories: dict[str, int] = {}
    while scored and len(selected) < p.limit:
        best_index, best_value = -1, -1.0
        for index, (candidate, ranked) in enumerate(scored):
            if creators.get(candidate.creator_id, 0) >= p.max_per_creator:
                continue
            adjusted = ranked.score - p.diversity_penalty * categories.get(candidate.category, 0) / max(1, len(selected))
            if adjusted > best_value:
                best_index, best_value = index, adjusted
        if best_index < 0:
            break
        candidate, ranked = scored.pop(best_index)
        ranked.score = round(best_value, 6)
        selected.append(ranked)
        creators[candidate.creator_id] = creators.get(candidate.creator_id, 0) + 1
        categories[candidate.category] = categories.get(candidate.category, 0) + 1
    return selected


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": "hybrid-content-v1"}


@app.post("/v1/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest) -> RecommendationResponse:
    return RecommendationResponse(items=_rank(request))
