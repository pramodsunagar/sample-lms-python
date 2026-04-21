from __future__ import annotations

AZURE_EVENTS: list[dict] = [
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


def get_relevant_events(skills_owned: str) -> list[dict]:
    """Return events whose tags match any of the user's skills.
    Falls back to top 15 events if skills_owned is empty or produces no matches.
    """
    if not skills_owned or not skills_owned.strip():
        return AZURE_EVENTS[:15]

    skill_tokens = [s.strip().lower() for s in skills_owned.split(",") if s.strip()]
    if not skill_tokens:
        return AZURE_EVENTS[:15]

    matched = [
        event
        for event in AZURE_EVENTS
        if any(
            token in tag or tag in token
            for token in skill_tokens
            for tag in event["tags"]
        )
    ]

    return (matched[:15] if matched else AZURE_EVENTS[:15])
