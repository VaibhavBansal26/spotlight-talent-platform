from datetime import datetime, timedelta, timezone

from app.main import Candidate, Interest, RecommendationRequest, _rank


def test_interest_match_beats_unrelated_content():
    now = datetime.now(timezone.utc)
    request = RecommendationRequest(
        user_id="user-1",
        interests=[Interest(topic="Dance", weight=1)],
        candidates=[
            Candidate(id="dance", category="Dance", creator_id="a", published_at=now, rating=4, completion_rate=.7),
            Candidate(id="film", category="Film", creator_id="b", published_at=now, rating=4, completion_rate=.7),
        ],
    )
    assert _rank(request)[0].content_id == "dance"


def test_seen_items_are_removed_and_old_items_decay():
    now = datetime.now(timezone.utc)
    request = RecommendationRequest(
        user_id="user-2",
        seen_content_ids=["seen"],
        candidates=[
            Candidate(id="seen", category="Music", creator_id="a", published_at=now),
            Candidate(id="old", category="Music", creator_id="b", published_at=now - timedelta(days=20)),
            Candidate(id="fresh", category="Music", creator_id="c", published_at=now),
        ],
    )
    ranked = _rank(request)
    assert [item.content_id for item in ranked] == ["fresh", "old"]
