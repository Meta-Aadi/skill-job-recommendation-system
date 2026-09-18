from pathlib import Path
from backend.recommender import JobRecommender

ROOT = Path(__file__).resolve().parents[1]
recommender = JobRecommender(ROOT / "data" / "jobs.csv")


def test_recommendations_return_results():
    results = recommender.recommend(["Python", "SQL", "Pandas"])
    assert len(results) > 0
    assert "match_percent" in results[0]


def test_results_are_sorted():
    results = recommender.recommend(["Python", "SQL"])
    scores = [item["match_percent"] for item in results]
    assert scores == sorted(scores, reverse=True)
