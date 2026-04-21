from __future__ import annotations

import httpx
from datetime import datetime, timedelta
from typing import Optional
from app.config import AZURE_EVENTS_CACHE_TTL_HOURS

# ---------------------------------------------------------------------------
# Static fallback — used when the live API is unreachable
# ---------------------------------------------------------------------------
_AZURE_EVENTS_FALLBACK: list[dict] = [
    {
        "title": "Microsoft Azure Virtual Training Day: Fundamentals",
        "date": "Apr 27-28, 2026",
        "url": "https://msevents.microsoft.com/event?id=1439795473",
        "tags": ["azure", "cloud", "fundamentals", "beginner"],
    },
    {
        "title": "Microsoft Azure Virtual Training Day: Data Fundamentals",
        "date": "Apr 23-25, 2026",
        "url": "https://msevents.microsoft.com/event?id=3001047949",
        "tags": ["data", "sql", "database", "fundamentals", "azure", "analytics"],
    },
    {
        "title": "Microsoft Virtual Training Day: Build Agentic AI Solutions with Azure AI Foundry",
        "date": "Apr 24, 2026",
        "url": "https://msevents.microsoft.com/event?id=795284837",
        "tags": ["ai", "ml", "azure", "developer", "openai", "agent", "python"],
    },
    {
        "title": "Microsoft Virtual Training Day: Develop generative AI apps with Azure AI Foundry",
        "date": "Apr 27-28, 2026",
        "url": "https://msevents.microsoft.com/event?id=4124362576",
        "tags": ["ai", "ml", "azure", "developer", "openai", "generative", "python"],
    },
    {
        "title": "Microsoft Azure Virtual Training Day: Migrate and Secure Windows Server and SQL Server Workloads",
        "date": "Apr 23-24, 2026",
        "url": "https://msevents.microsoft.com/event?id=1142853351",
        "tags": ["migration", "sql", "windows", "azure", "security", "infrastructure", "admin"],
    },
    {
        "title": "Microsoft Virtual Training Day: Introduction to Microsoft Security",
        "date": "Apr 23-24, 2026",
        "url": "https://msevents.microsoft.com/event?id=1768768676",
        "tags": ["security", "compliance", "identity", "azure"],
    },
    {
        "title": "Microsoft Virtual Training Day: Introduction to Microsoft Security",
        "date": "Apr 27-28, 2026",
        "url": "https://msevents.microsoft.com/event?id=1679390604",
        "tags": ["security", "compliance", "identity", "azure"],
    },
    {
        "title": "Microsoft Security Virtual Training Day: Implement Data Security with Microsoft Purview",
        "date": "Apr 27-28, 2026",
        "url": "https://msevents.microsoft.com/event?id=2333012384",
        "tags": ["security", "data", "compliance", "purview", "azure"],
    },
    {
        "title": "Microsoft Security Virtual Training Day: Strengthen Cloud Security with Microsoft Defender for Cloud",
        "date": "Apr 27-29, 2026",
        "url": "https://msevents.microsoft.com/event?id=1480374033",
        "tags": ["security", "cloud", "azure", "defender", "compliance"],
    },
    {
        "title": "Microsoft Virtual Training Day: Introduction to Microsoft 365, Copilot, and Agents",
        "date": "Apr 27, 2026",
        "url": "https://msevents.microsoft.com/event?id=599850483",
        "tags": ["copilot", "ai", "m365", "productivity", "agents"],
    },
    {
        "title": "Microsoft Virtual Training Day: Introduction to Microsoft Power Platform",
        "date": "Apr 27-29, 2026",
        "url": "https://msevents.microsoft.com/event?id=229996469",
        "tags": ["power platform", "data", "analytics", "low code", "automation"],
    },
    {
        "title": "Microsoft Virtual Training Day: Transform Customer Experiences with AI",
        "date": "Apr 28, 2026",
        "url": "https://msevents.microsoft.com/event?id=3103397276",
        "tags": ["ai", "customer", "dynamics", "crm", "azure"],
    },
]

# ---------------------------------------------------------------------------
# In-memory TTL cache
# ---------------------------------------------------------------------------
_cached_events: list[dict] = []
_cache_timestamp: Optional[datetime] = None

_MS_EVENTS_API = "https://events.microsoft.com/api/v1.0/event/search"
_MS_EVENTS_PARAMS = {
    "language": "English",
    "search": "Microsoft Virtual Training Day",
    "clientTimeZone": "1",
    "startTime": "All",
    "format": "json",
}

_TITLE_TAG_MAP: list[tuple[str, list[str]]] = [
    ("fundamentals", ["fundamentals", "beginner"]),
    ("azure", ["azure", "cloud"]),
    ("data", ["data"]),
    ("sql", ["sql", "database"]),
    ("ai foundry", ["ai", "ml", "openai", "azure", "developer"]),
    ("agentic", ["agent", "ai", "ml"]),
    ("generative", ["generative", "ai"]),
    ("security", ["security", "compliance"]),
    ("purview", ["purview", "data", "compliance"]),
    ("defender", ["defender", "security", "cloud"]),
    ("identity", ["identity", "security"]),
    ("windows server", ["windows", "infrastructure", "admin"]),
    ("migrate", ["migration"]),
    ("power platform", ["power platform", "low code", "automation"]),
    ("365", ["m365", "productivity"]),
    ("copilot", ["copilot", "ai", "productivity"]),
    ("dynamics", ["dynamics", "crm", "customer"]),
    ("python", ["python", "developer"]),
    ("infrastructure", ["infrastructure", "admin"]),
    ("analytics", ["analytics", "data"]),
]


def _infer_tags(title: str, description: str) -> list[str]:
    combined = (title + " " + description).lower()
    tags: list[str] = []
    seen: set[str] = set()
    for keyword, token_list in _TITLE_TAG_MAP:
        if keyword in combined:
            for t in token_list:
                if t not in seen:
                    tags.append(t)
                    seen.add(t)
    return tags or ["azure"]


def _format_date(start: str, end: str) -> str:
    try:
        s = datetime.fromisoformat(start.rstrip("Z"))
        s_day = s.strftime("%d").lstrip("0") or "0"
        label = f"{s.strftime('%b')} {s_day}, {s.strftime('%Y')}"
        if end and end != start:
            e = datetime.fromisoformat(end.rstrip("Z"))
            e_day = e.strftime("%d").lstrip("0") or "0"
            if s.month == e.month and s.year == e.year:
                label = f"{s.strftime('%b')} {s_day}-{e_day}, {s.strftime('%Y')}"
            else:
                label = f"{s.strftime('%b')} {s_day} – {e.strftime('%b')} {e_day}, {e.strftime('%Y')}"
        return label
    except Exception:
        return start[:10] if start else ""


async def fetch_azure_events(timeout: int = 10) -> list[dict]:
    """Fetch live Microsoft Virtual Training Day events from the MS Events API.

    Returns the static fallback list if the request fails or yields no results.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(_MS_EVENTS_API, params=_MS_EVENTS_PARAMS)
            resp.raise_for_status()
            data = resp.json()

        if isinstance(data, list):
            raw_events = data
        elif isinstance(data, dict):
            raw_events = (
                data.get("events")
                or data.get("value")
                or data.get("results")
                or []
            )
        else:
            raw_events = []

        if not raw_events:
            return _AZURE_EVENTS_FALLBACK

        events: list[dict] = []
        for item in raw_events:
            title: str = (
                item.get("title")
                or item.get("name")
                or item.get("eventTitle")
                or ""
            )
            url: str = (
                item.get("url")
                or item.get("registrationUrl")
                or item.get("eventUrl")
                or ""
            )
            start: str = (
                item.get("startDate")
                or item.get("startDateTime")
                or item.get("startTime")
                or ""
            )
            end: str = (
                item.get("endDate")
                or item.get("endDateTime")
                or item.get("endTime")
                or start
            )
            description: str = item.get("description") or item.get("summary") or ""
            raw_tags = item.get("tags") or item.get("categories") or []
            if raw_tags and isinstance(raw_tags, list):
                tags = [str(t).lower() for t in raw_tags]
            else:
                tags = _infer_tags(title, description)

            if not title or not url:
                continue

            events.append(
                {
                    "title": title,
                    "date": _format_date(start, end),
                    "url": url,
                    "tags": tags,
                }
            )

        return events if events else _AZURE_EVENTS_FALLBACK

    except Exception:
        return _AZURE_EVENTS_FALLBACK


async def _get_events_cached() -> list[dict]:
    global _cached_events, _cache_timestamp

    ttl = timedelta(hours=AZURE_EVENTS_CACHE_TTL_HOURS)
    now = datetime.utcnow()

    if _cached_events and _cache_timestamp and (now - _cache_timestamp) < ttl:
        return _cached_events

    events = await fetch_azure_events()
    _cached_events = events
    _cache_timestamp = now
    return _cached_events


async def get_relevant_events(skills_owned: str) -> list[dict]:
    """Return events whose tags match any of the user's skills.

    Fetches live data via the MS Events API (with TTL caching) and falls back
    to the static list on network errors. Returns up to 15 events.
    """
    all_events = await _get_events_cached()

    if not skills_owned or not skills_owned.strip():
        return all_events[:15]

    skill_tokens = [s.strip().lower() for s in skills_owned.split(",") if s.strip()]
    if not skill_tokens:
        return all_events[:15]

    matched = [
        event
        for event in all_events
        if any(
            token in tag or tag in token
            for token in skill_tokens
            for tag in event["tags"]
        )
    ]

    return matched[:15] if matched else all_events[:15]
