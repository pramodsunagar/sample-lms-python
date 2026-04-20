"""Tests for the AI service."""
import json
import pytest
from unittest.mock import patch, MagicMock


MOCK_ANALYSIS = {
    "skill_level": "intermediate",
    "search_terms": ["azure machine learning", "mlops"],
    "ms_learn_roles": ["ai-engineer", "data-scientist"],
    "ms_learn_products": ["azure-machine-learning"],
    "rationale": "As a Data Scientist targeting Azure ML, you need hands-on cloud ML skills.",
    "learning_sequence": ["Azure ML fundamentals", "MLOps pipelines", "Model deployment"],
}

MOCK_RANKED = [
    {"title": "Azure ML Fundamentals", "url": "https://learn.microsoft.com/az-900", "source": "MS Learn", "level": "beginner", "duration_hours": 5, "description": "Intro to Azure ML", "tags": ["azure", "ml"], "ai_score": 9.2, "ai_reason": "Highly relevant"},
]

MOCK_WEEKLY = [
    {"week": 1, "theme": "Azure ML Basics", "courses": ["https://learn.microsoft.com/az-900"]},
]


def _mock_ollama_response(payload: dict) -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"response": json.dumps(payload)}
    return resp


def test_analyze_skill_gap_returns_dict():
    with patch("app.services.ai_service.requests.post", return_value=_mock_ollama_response(MOCK_ANALYSIS)):
        from app.services import ai_service
        result = ai_service.analyze_skill_gap("Data Scientist", "Azure Machine Learning")
    assert isinstance(result, dict)
    assert "skill_level" in result
    assert "search_terms" in result


def test_analyze_skill_gap_fallback_on_invalid_json():
    bad_resp = MagicMock()
    bad_resp.status_code = 200
    bad_resp.json.return_value = {"response": "This is not JSON"}
    with patch("app.services.ai_service.requests.post", return_value=bad_resp):
        from app.services import ai_service
        result = ai_service.analyze_skill_gap("Engineer", "Kubernetes")
    assert isinstance(result, dict)
    assert "skill_level" in result  # fallback defaults


def test_rank_and_curate_returns_list():
    courses = [
        {"title": "Azure Basics", "url": "https://learn.microsoft.com/1", "source": "MS Learn", "level": "beginner", "duration_hours": 5, "description": "Intro", "tags": ["azure"]},
    ]
    with patch("app.services.ai_service.requests.post", return_value=_mock_ollama_response(MOCK_RANKED)):
        from app.services import ai_service
        result = ai_service.rank_and_curate("Data Scientist", "Azure ML", "beginner", courses)
    assert isinstance(result, list)


def test_generate_learning_sequence_returns_weeks():
    courses = MOCK_RANKED
    with patch("app.services.ai_service.requests.post", return_value=_mock_ollama_response(MOCK_WEEKLY)):
        from app.services import ai_service
        result = ai_service.generate_learning_sequence("Azure ML", courses)
    assert isinstance(result, list)


def test_analyze_skill_gap_handles_ollama_down():
    import requests as _requests
    with patch("app.services.ai_service.requests.post", side_effect=_requests.exceptions.ConnectionError("Ollama not running")):
        from app.services import ai_service
        result = ai_service.analyze_skill_gap("Engineer", "Docker")
    assert isinstance(result, dict)
    assert result.get("skill_level") == "beginner"  # safe default
