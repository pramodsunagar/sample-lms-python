"""Tests for the aggregator service."""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock


def _make_course(source, title, tags=None):
    return {
        "title": title,
        "url": f"https://example.com/{title.replace(' ', '-').lower()}",
        "source": source,
        "level": "beginner",
        "duration_hours": 5,
        "description": f"Course about {title}",
        "tags": tags or [],
    }


@pytest.mark.asyncio
async def test_aggregate_deduplicates():
    """Courses with the same URL from multiple sources are deduplicated."""
    shared_url = "https://example.com/shared"
    course_a = {"title": "Shared Course", "url": shared_url, "source": "MS Learn", "level": "beginner", "duration_hours": 3, "description": "", "tags": []}
    course_b = {**course_a, "source": "edX"}

    with (
        patch("app.services.ms_learn.fetch_courses", new_callable=AsyncMock, return_value=[course_a]),
        patch("app.services.coursera.fetch_courses", new_callable=AsyncMock, return_value=[course_b]),
        patch("app.services.static_catalog.get_all", return_value=[]),
    ):
        from app.services import aggregator
        results = await aggregator.aggregate(roles=["developer"], levels=["beginner"], products=["azure"], search_terms=["python"])

    urls = [c["url"] for c in results]
    assert urls.count(shared_url) == 1, "Duplicate URLs should be removed"


@pytest.mark.asyncio
async def test_aggregate_returns_courses_from_all_sources():
    ms = _make_course("MS Learn", "Azure Fundamentals")
    cs = _make_course("Coursera", "Python Basics")
    st = _make_course("edX", "Linux Intro")

    with (
        patch("app.services.ms_learn.fetch_courses", new_callable=AsyncMock, return_value=[ms]),
        patch("app.services.coursera.fetch_courses", new_callable=AsyncMock, return_value=[cs]),
        patch("app.services.static_catalog.get_all", return_value=[st]),
    ):
        from app.services import aggregator
        results = await aggregator.aggregate(roles=["developer"], levels=["beginner"], products=["azure"], search_terms=["python"])

    sources = {c["source"] for c in results}
    assert "MS Learn" in sources
    assert "Coursera" in sources
    assert "edX" in sources


@pytest.mark.asyncio
async def test_aggregate_handles_source_exception():
    """If one source raises, others still succeed."""
    cs = _make_course("Coursera", "Python Basics")

    with (
        patch("app.services.ms_learn.fetch_courses", new_callable=AsyncMock, side_effect=Exception("network error")),
        patch("app.services.coursera.fetch_courses", new_callable=AsyncMock, return_value=[cs]),
        patch("app.services.static_catalog.get_all", return_value=[]),
    ):
        from app.services import aggregator
        results = await aggregator.aggregate(roles=["developer"], levels=["beginner"], products=["azure"], search_terms=["python"])

    assert any(c["source"] == "Coursera" for c in results)
