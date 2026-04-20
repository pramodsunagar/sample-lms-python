"""Tests for the static catalog loader."""
import os
import json
import pytest


def test_get_google_skills_courses(tmp_path, monkeypatch):
    catalog = [
        {"title": "GCP Basics", "url": "https://example.com/gcp", "source": "Google Skills Boost",
         "level": "beginner", "duration_hours": 8, "description": "GCP intro", "tags": ["gcp"]}
    ]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "google_skills_catalog.json").write_text(json.dumps(catalog))
    (data_dir / "freecodecamp_catalog.json").write_text("[]")
    (data_dir / "edx_catalog.json").write_text("[]")

    import app.services.static_catalog as sc
    monkeypatch.setattr(sc, "DATA_DIR", str(data_dir))
    results = sc.get_all()
    assert len(results) == 1
    assert results[0]["title"] == "GCP Basics"


def test_get_all_merges_catalogs(tmp_path, monkeypatch):
    google = [{"title": "GCP", "url": "https://g.com/1", "source": "Google Skills Boost", "level": "beginner", "duration_hours": 5, "description": "", "tags": []}]
    fcc = [{"title": "FCC JS", "url": "https://fcc.com/1", "source": "freeCodeCamp", "level": "beginner", "duration_hours": 300, "description": "", "tags": []}]
    edx = [{"title": "edX CS50", "url": "https://edx.com/1", "source": "edX", "level": "beginner", "duration_hours": 100, "description": "", "tags": []}]

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "google_skills_catalog.json").write_text(json.dumps(google))
    (data_dir / "freecodecamp_catalog.json").write_text(json.dumps(fcc))
    (data_dir / "edx_catalog.json").write_text(json.dumps(edx))

    import app.services.static_catalog as sc
    monkeypatch.setattr(sc, "DATA_DIR", str(data_dir))
    results = sc.get_all()
    assert len(results) == 3
    sources = {c["source"] for c in results}
    assert sources == {"Google Skills Boost", "freeCodeCamp", "edX"}


def test_search_filters_by_keyword(tmp_path, monkeypatch):
    catalog = [
        {"title": "Python for Data Science", "url": "https://edx.com/py", "source": "edX", "level": "intermediate", "duration_hours": 20, "description": "Learn pandas and numpy", "tags": ["python", "data science"]},
        {"title": "Linux Fundamentals", "url": "https://edx.com/linux", "source": "edX", "level": "beginner", "duration_hours": 10, "description": "Learn linux command line", "tags": ["linux"]},
    ]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "google_skills_catalog.json").write_text("[]")
    (data_dir / "freecodecamp_catalog.json").write_text("[]")
    (data_dir / "edx_catalog.json").write_text(json.dumps(catalog))

    import app.services.static_catalog as sc
    monkeypatch.setattr(sc, "DATA_DIR", str(data_dir))
    results = sc.search(["python"])
    assert all("python" in c["title"].lower() or "python" in " ".join(c["tags"]).lower() for c in results)
    assert len(results) == 1
