"""
API Discovery Routes — REST endpoints for searching and browsing APIs.
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import APIEntry, APICategory, HealthCheck
from schemas import (
    DiscoverRequest, DiscoverResponse,
    APISummary, APIDetail, CategoryOut,
    HealthCheckResult,
)
from discovery.engine import discover_apis
from discovery.verifier import verify_api
from discovery.ranking import score_breakdown
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Discovery"])


@router.post("/discover", response_model=DiscoverResponse)
def discover(request: DiscoverRequest, db: Session = Depends(get_db)):
    """
    🔍 Discover APIs for your application idea.

    Send an application idea (e.g., "I am building a travel planner app")
    and get categorized API recommendations ranked by composite score.
    """
    result = discover_apis(request.idea, db)
    return result


@router.get("/apis")
def list_apis(
    category: str | None = Query(None, description="Filter by category name"),
    free_only: bool = Query(False, description="Show only APIs with free tiers"),
    search: str | None = Query(None, description="Search APIs by name or tag"),
    sort_by: str = Query("composite_score", description="Sort field"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """📋 Browse the API catalog with filters and sorting."""
    query = db.query(APIEntry).filter(APIEntry.is_active == True)

    if category:
        cat = db.query(APICategory).filter_by(name=category).first()
        if cat:
            query = query.filter(APIEntry.category_id == cat.id)

    if free_only:
        query = query.filter(APIEntry.free_tier == True)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            APIEntry.name.ilike(search_term) |
            APIEntry.description.ilike(search_term) |
            APIEntry.provider.ilike(search_term)
        )

    # Sort
    sort_field = getattr(APIEntry, sort_by, APIEntry.composite_score)
    query = query.order_by(sort_field.desc())

    total = query.count()
    apis = query.offset(offset).limit(limit).all()

    results = []
    for api in apis:
        cat = db.query(APICategory).filter_by(id=api.category_id).first()
        results.append({
            "id": api.id,
            "name": api.name,
            "slug": api.slug,
            "provider": api.provider,
            "category": cat.display_name if cat else "",
            "description": api.description,
            "free_tier": api.free_tier,
            "pricing_model": api.pricing_model,
            "composite_score": api.composite_score,
            "is_active": api.is_active,
            "tags": api.tags or [],
        })

    return {"total": total, "apis": results}


@router.get("/apis/{slug}")
def get_api_detail(slug: str, db: Session = Depends(get_db)):
    """📖 Get detailed information about a specific API."""
    api = db.query(APIEntry).filter_by(slug=slug).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    cat = db.query(APICategory).filter_by(id=api.category_id).first()

    detail = {
        "id": api.id,
        "name": api.name,
        "slug": api.slug,
        "provider": api.provider,
        "category": cat.display_name if cat else "",
        "description": api.description,
        "free_tier": api.free_tier,
        "pricing_model": api.pricing_model,
        "pricing_details": api.pricing_details,
        "auth_type": api.auth_type,
        "documentation_url": api.documentation_url,
        "base_url": api.base_url,
        "sdk_languages": api.sdk_languages or [],
        "request_limit": api.request_limit,
        "github_url": api.github_url,
        "composite_score": api.composite_score,
        "popularity_score": api.popularity_score,
        "doc_quality_score": api.doc_quality_score,
        "reliability_score": api.reliability_score,
        "latency_score": api.latency_score,
        "pricing_score": api.pricing_score,
        "alternatives": api.alternatives or [],
        "tags": api.tags or [],
        "is_active": api.is_active,
        "last_verified": api.last_verified,
        "last_response_ms": api.last_response_ms,
        "score_breakdown": score_breakdown({
            "name": api.name,
            "composite_score": api.composite_score,
            "popularity_score": api.popularity_score,
            "doc_quality_score": api.doc_quality_score,
            "reliability_score": api.reliability_score,
            "pricing_score": api.pricing_score,
            "latency_score": api.latency_score,
        }),
    }
    return detail


@router.post("/verify/{slug}")
async def verify_api_endpoint(slug: str, db: Session = Depends(get_db)):
    """🔍 Run a live health check on an API."""
    api = db.query(APIEntry).filter_by(slug=slug).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    result = await verify_api(
        base_url=api.base_url,
        documentation_url=api.documentation_url,
        api_name=api.name,
    )

    # Save health check
    check = HealthCheck(
        api_entry_id=api.id,
        is_reachable=result["is_reachable"],
        status_code=result["status_code"],
        response_ms=result["response_ms"],
        doc_reachable=result["doc_reachable"],
        error=result["error"],
    )
    db.add(check)

    # Update API entry
    api.last_verified = datetime.utcnow()
    api.last_response_ms = result["response_ms"]
    db.commit()

    return result


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """📁 List all API categories with counts."""
    categories = db.query(APICategory).all()
    result = []
    for cat in categories:
        count = db.query(APIEntry).filter_by(category_id=cat.id).count()
        result.append({
            "id": cat.id,
            "name": cat.name,
            "display_name": cat.display_name,
            "description": cat.description,
            "icon": cat.icon,
            "api_count": count,
        })
    return result


@router.get("/ranking/{slug}")
def get_ranking(slug: str, db: Session = Depends(get_db)):
    """📊 Get detailed scoring breakdown for an API."""
    api = db.query(APIEntry).filter_by(slug=slug).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    return score_breakdown({
        "name": api.name,
        "composite_score": api.composite_score,
        "popularity_score": api.popularity_score,
        "doc_quality_score": api.doc_quality_score,
        "reliability_score": api.reliability_score,
        "pricing_score": api.pricing_score,
        "latency_score": api.latency_score,
    })
