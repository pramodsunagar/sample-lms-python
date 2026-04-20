import json
import re
import ollama
from app.config import OLLAMA_HOST, OLLAMA_MODEL

_client = ollama.Client(host=OLLAMA_HOST)

ANALYZE_PROMPT = """You are a learning advisor AI. Given a user's current role and a skill they want to learn, return a JSON object with the following fields:
- skill_level: estimated starting level for this skill ("beginner", "intermediate", or "advanced")
- search_terms: list of 3-5 keyword strings suitable for searching learning catalogs
- ms_learn_roles: list of 1-3 Microsoft Learn role identifiers (e.g. "developer", "data-engineer", "ai-engineer", "solution-architect", "devops-engineer", "security-engineer", "administrator", "business-analyst", "data-scientist", "database-administrator")
- ms_learn_products: list of 1-3 Microsoft Learn product identifiers (e.g. "azure", "power-bi", "github", "fabric", "azure-databricks", "azure-machine-learning")
- learning_sequence: ordered list of 3-5 topic strings representing the recommended learning progression
- rationale: 1-2 sentence explanation of the recommended path

Return ONLY valid JSON, no markdown, no explanation.

User role: {role}
Skill to learn: {target_skill}
"""

RANK_PROMPT = """You are a learning path curator. Given a user's role and target skill, select and rank the most relevant courses from the provided list.

User role: {role}
Target skill: {target_skill}
Skill level: {skill_level}

Available courses (JSON array):
{courses_json}

Return a JSON array of the top courses (maximum 15). Each item must have all original fields plus a "relevance_note" string (1 sentence explaining why this course fits). Order them from most to least relevant. Return ONLY valid JSON array.
"""

SEQUENCE_PROMPT = """You are a learning journey designer. Group the following courses into a weekly learning plan.

Target skill: {target_skill}
Courses (JSON array):
{courses_json}

Return a JSON array of weekly groups. Each group: {{"week": "Week 1-2", "theme": "theme title", "course_urls": ["url1", "url2"]}}
Return ONLY valid JSON array.
"""


def _extract_json(text: str):
    """Extract JSON from LLM output that may contain extra text."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None


def analyze_skill_gap(role: str, target_skill: str) -> dict:
    """Call Ollama to analyze the skill gap and return search metadata."""
    prompt = ANALYZE_PROMPT.format(role=role, target_skill=target_skill)
    try:
        response = _client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"]
        result = _extract_json(content)
        if result and isinstance(result, dict):
            return result
    except Exception:
        pass
    return {
        "skill_level": "beginner",
        "search_terms": [target_skill],
        "ms_learn_roles": ["developer"],
        "ms_learn_products": ["azure"],
        "learning_sequence": [target_skill],
        "rationale": f"Learning path for {target_skill} tailored for a {role}.",
    }


def rank_and_curate(role: str, target_skill: str, skill_level: str, courses: list) -> list:
    """Call Ollama to rank and select the most relevant courses."""
    if not courses:
        return []
    courses_json = json.dumps(courses, ensure_ascii=False)
    prompt = RANK_PROMPT.format(
        role=role,
        target_skill=target_skill,
        skill_level=skill_level,
        courses_json=courses_json[:6000],
    )
    try:
        response = _client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"]
        result = _extract_json(content)
        if result and isinstance(result, list):
            return result[:15]
    except Exception:
        pass
    for c in courses[:15]:
        c.setdefault("relevance_note", "")
    return courses[:15]


def generate_learning_sequence(target_skill: str, courses: list) -> list:
    """Call Ollama to group courses into a weekly sequence."""
    if not courses:
        return []
    courses_json = json.dumps(
        [{"title": c.get("title"), "url": c.get("url")} for c in courses],
        ensure_ascii=False,
    )
    prompt = SEQUENCE_PROMPT.format(target_skill=target_skill, courses_json=courses_json)
    try:
        response = _client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"]
        result = _extract_json(content)
        if result and isinstance(result, list):
            return result
    except Exception:
        pass
    return [{"week": "Full Path", "theme": target_skill, "course_urls": [c.get("url") for c in courses]}]
