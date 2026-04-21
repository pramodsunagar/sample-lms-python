from __future__ import annotations

AZURE_EVENTS: list[dict] = [
    {
        "title": "Azure Fundamentals (AZ-900) – 2-Day Virtual Training",
        "date": "May 6–7, 2026",
        "url": "https://learn.microsoft.com/en-us/training/courses/az-900t00",
        "tags": ["azure", "cloud", "fundamentals", "beginner"],
    },
    {
        "title": "AI Fundamentals (AI-900) – Virtual Training Day",
        "date": "May 13–14, 2026",
        "url": "https://learn.microsoft.com/en-us/training/courses/ai-900t00",
        "tags": ["ai", "ml", "machine learning", "fundamentals", "azure", "python", "developer"],
    },
    {
        "title": "Azure Data Fundamentals (DP-900) – Virtual Training Day",
        "date": "May 20–21, 2026",
        "url": "https://learn.microsoft.com/en-us/training/courses/dp-900t00",
        "tags": ["data", "sql", "database", "fundamentals", "azure"],
    },
    {
        "title": "Azure AI Services & Azure OpenAI – Virtual Training Day",
        "date": "May 27–28, 2026",
        "url": "https://learn.microsoft.com/en-us/training/paths/develop-ai-solutions-azure-openai/",
        "tags": ["openai", "ai", "ml", "cognitive", "azure", "developer", "python"],
    },
    {
        "title": "Copilot for Azure – Virtual Training Day",
        "date": "Jun 3–4, 2026",
        "url": "https://learn.microsoft.com/en-us/training/browse/?terms=copilot&products=azure",
        "tags": ["copilot", "ai", "azure", "developer", "productivity"],
    },
    {
        "title": "Azure Administrator (AZ-104) – 3-Day Virtual Training",
        "date": "Jun 10–12, 2026",
        "url": "https://learn.microsoft.com/en-us/training/courses/az-104t00",
        "tags": ["admin", "administrator", "infrastructure", "azure", "cloud"],
    },
    {
        "title": "Developing Solutions for Azure (AZ-204) – Virtual Training Day",
        "date": "Jun 17–19, 2026",
        "url": "https://learn.microsoft.com/en-us/training/courses/az-204t00",
        "tags": ["developer", "python", "dev", "azure", "api", "serverless", "cloud"],
    },
    {
        "title": "Azure Security Technologies (AZ-500) – Virtual Training Day",
        "date": "Jun 24–26, 2026",
        "url": "https://learn.microsoft.com/en-us/training/courses/az-500t00",
        "tags": ["security", "compliance", "zero trust", "azure", "identity"],
    },
    {
        "title": "GitHub Advanced Security – Virtual Training Day",
        "date": "Jul 1–2, 2026",
        "url": "https://learn.microsoft.com/en-us/training/paths/github-advanced-security/",
        "tags": ["github", "security", "devops", "developer", "compliance"],
    },
    {
        "title": "DevOps with GitHub & Azure (AZ-400) – Virtual Training Day",
        "date": "Jul 8–10, 2026",
        "url": "https://learn.microsoft.com/en-us/training/courses/az-400t00",
        "tags": ["devops", "github", "git", "ci/cd", "azure", "developer"],
    },
    {
        "title": "Azure Migrate & Modernize – Virtual Training Day",
        "date": "Jul 15–16, 2026",
        "url": "https://learn.microsoft.com/en-us/training/paths/migrate-to-azure/",
        "tags": ["migration", "cloud", "azure", "infrastructure", "modernize"],
    },
    {
        "title": "Microsoft Fabric & Analytics – Virtual Training Day",
        "date": "Jul 22–23, 2026",
        "url": "https://learn.microsoft.com/en-us/training/browse/?products=fabric",
        "tags": ["data", "analytics", "fabric", "sql", "azure", "ml"],
    },
    {
        "title": "Azure Cost Optimization – Virtual Training Day",
        "date": "Aug 5–6, 2026",
        "url": "https://learn.microsoft.com/en-us/training/paths/control-spending-manage-bills/",
        "tags": ["cost", "finops", "azure", "cloud", "infrastructure"],
    },
    {
        "title": "Azure Well-Architected & Reliability – Virtual Training Day",
        "date": "Aug 12–13, 2026",
        "url": "https://learn.microsoft.com/en-us/training/paths/azure-well-architected-framework/",
        "tags": ["architecture", "reliability", "azure", "cloud", "infrastructure", "admin"],
    },
]


def get_relevant_events(skills_owned: str) -> list[dict]:
    """Return events whose tags match any of the user's skills.

    Falls back to all events if skills_owned is empty or produces no matches.
    """
    if not skills_owned or not skills_owned.strip():
        return AZURE_EVENTS

    skill_tokens = [s.strip().lower() for s in skills_owned.split(",") if s.strip()]
    if not skill_tokens:
        return AZURE_EVENTS

    matched = [
        event
        for event in AZURE_EVENTS
        if any(
            token in tag or tag in token
            for token in skill_tokens
            for tag in event["tags"]
        )
    ]

    return matched if matched else AZURE_EVENTS
