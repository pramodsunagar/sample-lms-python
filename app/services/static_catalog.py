import json
import os
from typing import List
from app.services.ms_learn import CourseResult

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _load(filename: str) -> list:
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def search(query_terms: List[str], source_files: List[str] = None) -> List[dict]:
    """Search all static catalogs for courses matching any of the query terms."""
    if source_files is None:
        source_files = [
            "google_skills_catalog.json",
            "freecodecamp_catalog.json",
            "edx_catalog.json",
        ]
    results = []
    for fname in source_files:
        items = _load(fname)
        for item in items:
            # Skip entries without an absolute URL
            raw_url = item.get("url", "")
            if not raw_url.startswith("http"):
                continue
            combined = (
                item.get("title", "")
                + " "
                + item.get("description", item.get("summary", ""))
                + " "
                + " ".join(item.get("tags", []))
            ).lower()
            if not query_terms or any(t.lower() in combined for t in query_terms):
                # Safely compute duration_minutes; avoid None * 60 TypeError
                duration_hours = item.get("duration_hours") or 0
                duration_minutes = item.get("duration_minutes") or int(duration_hours * 60)
                results.append(
                    CourseResult(
                        title=item.get("title", ""),
                        url=raw_url,
                        source=item.get("source", ""),
                        level=item.get("level", "beginner"),
                        duration_minutes=duration_minutes,
                        summary=item.get("description", item.get("summary", "")),
                        roles=item.get("roles", []),
                        products=item.get("tags", []),
                        prerequisites=item.get("prerequisites", ""),
                    ).to_dict()
                )
    return results
