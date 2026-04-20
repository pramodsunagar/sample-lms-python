import httpx
from typing import List
from app.services.ms_learn import CourseResult

COURSERA_API = "https://api.coursera.org/api/courses.v1"


async def fetch_courses(search_terms: List[str], limit: int = 100, timeout: int = 15) -> List[dict]:
    """Fetch courses from Coursera public catalog and filter by search terms."""
    params = {
        "fields": "name,slug,description,primaryLanguages,workload",
        "limit": limit,
    }
    results: List[dict] = []
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(COURSERA_API, params=params)
            resp.raise_for_status()
            data = resp.json()
            elements = data.get("elements", [])
            for item in elements:
                name: str = item.get("name", "")
                slug: str = item.get("slug", "")
                description: str = item.get("description", "")
                workload: str = item.get("workload", "")
                # Build absolute URL from slug; skip if no slug
                if not slug:
                    continue
                url = f"https://www.coursera.org/learn/{slug}"
                combined = (name + " " + description).lower()
                if search_terms:
                    if not any(t.lower() in combined for t in search_terms):
                        continue
                # Estimate duration from workload string
                duration = 0
                if workload and "hour" in workload.lower():
                    import re
                    nums = re.findall(r'\d+', workload)
                    if nums:
                        duration = int(nums[0]) * 60
                results.append(
                    CourseResult(
                        title=name,
                        url=url,
                        source="Coursera",
                        level="beginner",
                        duration_minutes=duration,
                        summary=description[:300],
                        roles=[],
                        products=[],
                        prerequisites="",
                    ).to_dict()
                )
    except Exception:
        pass
    return results
