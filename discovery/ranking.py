"""
API Ranking & Scoring Algorithm.

Composite Score = weighted average of:
  - Popularity     (30%)  — GitHub stars, downloads, dev adoption
  - Documentation  (20%)  — quality, completeness, examples
  - Reliability    (20%)  — uptime, consistency, error rates
  - Pricing        (15%)  — free tier generosity, value for money
  - Latency        (15%)  — response speed, global edge coverage
"""
from config import SCORING_WEIGHTS


def compute_composite_score(
    popularity:    float,
    documentation: float,
    reliability:   float,
    pricing:       float,
    latency:       float,
) -> float:
    """Return a 0-100 composite score."""
    return round(
        popularity    * SCORING_WEIGHTS["popularity"]    +
        documentation * SCORING_WEIGHTS["documentation"] +
        reliability   * SCORING_WEIGHTS["reliability"]   +
        pricing       * SCORING_WEIGHTS["pricing"]       +
        latency       * SCORING_WEIGHTS["latency"],
        2
    )


def rank_apis(apis: list[dict], sort_by: str = "composite_score", ascending: bool = False) -> list[dict]:
    """Sort a list of API dicts by any score field."""
    valid_keys = {
        "composite_score", "popularity_score", "doc_quality_score",
        "reliability_score", "pricing_score", "latency_score",
    }
    key = sort_by if sort_by in valid_keys else "composite_score"
    return sorted(apis, key=lambda a: a.get(key, 0), reverse=not ascending)


def score_breakdown(api: dict) -> dict:
    """Return a human-readable scoring breakdown for one API."""
    weights = SCORING_WEIGHTS
    return {
        "api_name": api.get("name", ""),
        "composite_score": api.get("composite_score", 0),
        "breakdown": {
            "popularity":    {"score": api.get("popularity_score", 0),    "weight": weights["popularity"],    "contribution": round(api.get("popularity_score", 0) * weights["popularity"], 2)},
            "documentation": {"score": api.get("doc_quality_score", 0),   "weight": weights["documentation"], "contribution": round(api.get("doc_quality_score", 0) * weights["documentation"], 2)},
            "reliability":   {"score": api.get("reliability_score", 0),   "weight": weights["reliability"],   "contribution": round(api.get("reliability_score", 0) * weights["reliability"], 2)},
            "pricing":       {"score": api.get("pricing_score", 0),       "weight": weights["pricing"],       "contribution": round(api.get("pricing_score", 0) * weights["pricing"], 2)},
            "latency":       {"score": api.get("latency_score", 0),       "weight": weights["latency"],       "contribution": round(api.get("latency_score", 0) * weights["latency"], 2)},
        },
        "formula": "composite = (popularity×0.30) + (documentation×0.20) + (reliability×0.20) + (pricing×0.15) + (latency×0.15)",
    }
