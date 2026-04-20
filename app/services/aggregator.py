import asyncio
from typing import List
from app.services.ms_learn import fetch_learning_paths
from app.services.coursera import fetch_courses
from app.services.static_catalog import search as static_search


async def aggregate(
    roles: List[str],
    levels: List[str],
    products: List[str],
    search_terms: List[str],
) -> List[dict]:
    """Fetch from all sources in parallel, deduplicate by URL, return merged list."""
    ms_task = fetch_learning_paths(roles, levels, products, search_terms)
    coursera_task = fetch_courses(search_terms)

    ms_results, coursera_results = await asyncio.gather(ms_task, coursera_task)
    static_results = static_search(search_terms)

    all_results = ms_results + coursera_results + static_results

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for course in all_results:
        url = course.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(course)

    return unique
