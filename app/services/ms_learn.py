import httpx
from dataclasses import dataclass, asdict
from typing import List

MS_LEARN_API = "https://learn.microsoft.com/api/catalog/"


@dataclass
class CourseResult:
    title: str
    url: str
    source: str
    level: str
    duration_minutes: int
    summary: str
    roles: list
    products: list
    relevance_note: str = ""
    prerequisites: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


async def fetch_learning_paths(
    roles: List[str],
    levels: List[str],
    products: List[str],
    search_terms: List[str],
    timeout: int = 15,
) -> List[dict]:
    """Fetch learning paths from Microsoft Learn catalog API."""
    params = {
        "locale": "en-us",
        "type": "learningPaths",
    }
    if roles:
        params["roles"] = ",".join(roles)
    if levels:
        params["levels"] = ",".join(levels)
    if products:
        params["products"] = ",".join(products)

    results: List[dict] = []
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(MS_LEARN_API, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("learningPaths", [])
            for item in items:
                title: str = item.get("title", "")
                summary: str = item.get("summary", "")
                url: str = item.get("url", "")
                if not url:
                    # Fall back to uid field when url is missing
                    uid: str = item.get("uid", "")
                    if uid:
                        url = f"https://learn.microsoft.com/en-us/training/{uid}"
                elif not url.startswith("http"):
                    url = f"https://learn.microsoft.com{url}"
                levels_list = item.get("levels", [])
                duration = item.get("duration_in_minutes", 0) or 0
                item_roles = item.get("roles", [])
                item_products = item.get("products", [])
                prerequisites: str = item.get("prerequisites", "")

                # Keyword relevance filter
                combined_text = (title + " " + summary).lower()
                if search_terms:
                    match = any(term.lower() in combined_text for term in search_terms)
                    if not match:
                        continue

                results.append(
                    CourseResult(
                        title=title,
                        url=url,
                        source="Microsoft Learn",
                        level=levels_list[0] if levels_list else "beginner",
                        duration_minutes=duration,
                        summary=summary,
                        roles=item_roles,
                        products=item_products,
                        prerequisites=prerequisites,
                    ).to_dict()
                )
    except Exception:
        pass
    return results
