# 🚀 AI Learning Experience Platform (LXP)

An AI-powered **Learning Experience Platform (LXP)** built with **FastAPI**, **Ollama (local LLM)**, **SQLite**, and **Bootstrap 5**.

The platform aggregates learning content from multiple providers, uses a **local AI model** to personalize learning paths, and enables users to track and manage their progress efficiently.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Routes](#-api-routes)
- [Course Sources](#-course-sources)
- [AI Processing Pipeline](#-ai-processing-pipeline)
- [Setup & Installation](#-setup--installation)
- [Running the Application](#-running-the-application)
- [Environment Variables](#-environment-variables)
- [Running Tests](#-running-tests)
- [Known Limitations](#-known-limitations)
- [Future Enhancements](#-future-enhancements)

---

## 📖 Overview

The **AI LXP** analyzes a user’s current role and desired skill, then automatically:

1. Performs **skill-gap analysis** using a local LLM (**Ollama / Mistral**)
2. **Aggregates relevant courses** from multiple learning providers in parallel
3. **Ranks and curates** the most relevant learning resources
4. Generates a **personalized weekly learning roadmap**

Users can:

- Save learning paths
- Track course progress
- Update learning status
- Remove outdated paths
- Log removal comments for auditing

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **User Authentication** | Secure registration/login with bcrypt password hashing |
| **User Profile Management** | Manage role, skills, learning goals, and experience level |
| **AI Skill Gap Analysis** | Identify skill gaps and generate role-specific learning paths |
| **Course Aggregation** | Fetch courses from multiple providers in parallel |
| **AI Course Ranking** | AI-based ranking and relevance scoring |
| **Weekly Learning Plan** | Auto-generated weekly learning roadmap |
| **Progress Tracking** | Track status from Not Started → Completed |
| **Dashboard** | Manage all saved learning paths |
| **Audit Logging** | Path deletion comments stored for traceability |
| **Offline Static Catalogs** | Supports JSON-based course catalogs |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Framework** | FastAPI `0.111.0` |
| **ASGI Server** | Uvicorn `0.29.0` |
| **Templating** | Jinja2 `3.1.4` |
| **Database** | SQLite + SQLAlchemy `>=2.0.36` |
| **Authentication** | bcrypt + SessionMiddleware |
| **AI / LLM** | Ollama `0.2.1` + `mistral` |
| **HTTP Client** | HTTPX `0.27.0` |
| **Frontend** | Bootstrap 5 + Bootstrap Icons |
| **Testing** | Pytest + pytest-asyncio |
| **Python Version** | 3.13 |

---

## 📂 Project Structure

```text
Sample-LMS-Python/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database/
│   │   └── db.py
│   ├── models/
│   │   ├── user.py
│   │   └── learning.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── profile.py
│   │   └── learning.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── aggregator.py
│   │   ├── ms_learn.py
│   │   ├── coursera.py
│   │   └── static_catalog.py
│   └── templates/
├── data/
├── static/
├── tests/
├── .env
├── .env.example
├── requirements.txt
└── lxp.db
```

---

## 🗄 Database Schema

### `users`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| username | VARCHAR(80) | Unique |
| email | VARCHAR(120) | Unique |
| hashed_password | VARCHAR(255) | bcrypt hashed |
| created_at | DATETIME | UTC timestamp |

---

### `user_profiles`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| user_id | INTEGER | Foreign key |
| current_role | VARCHAR(120) | Current designation |
| skills_owned | TEXT | Comma-separated list |
| learning_goal | TEXT | Target skill |
| experience_level | VARCHAR(30) | beginner/intermediate/advanced |

---

### `saved_paths`

Stores user learning plans.

---

### `course_progress`

Tracks learning progress per course.

---

### `path_removal_logs`

Stores deleted learning path audit logs.

---

## 🌐 API Routes

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/register` | Registration page |
| POST | `/register` | Create account |
| GET | `/login` | Login page |
| POST | `/login` | Authenticate user |
| GET | `/logout` | Logout user |

---

### Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile` | View profile |
| POST | `/profile` | Update profile |

---

### Learning

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/generate` | Path generator |
| POST | `/generate` | Generate AI roadmap |
| POST | `/save` | Save roadmap |
| GET | `/dashboard` | View saved paths |
| POST | `/progress` | Update progress |
| POST | `/remove-path` | Delete saved path |

---

## 📚 Course Sources

| Source | Type | Fetch Mode |
|--------|------|------------|
| Microsoft Learn | Live API | HTTP API |
| Coursera | Live API | HTTP API |
| Google Skills Boost | Static JSON | Local file |
| freeCodeCamp | Static JSON | Local file |
| edX | Static JSON | Local file |

---

## 🤖 AI Processing Pipeline

```text
User Input
   ↓
Skill Gap Analysis
   ↓
Parallel Course Aggregation
   ↓
AI Ranking & Curation
   ↓
Weekly Learning Plan Generation
   ↓
Save to Dashboard
```

### AI Functions

| Function | Purpose |
|----------|---------|
| `analyze_skill_gap()` | Identify learning needs |
| `rank_and_curate()` | Rank top learning resources |
| `generate_learning_sequence()` | Create weekly roadmap |

---

## ⚙ Setup & Installation

### Prerequisites

- Python `3.13`
- Ollama installed
- Mistral model pulled

```bash
ollama pull mistral
```

---

### Installation Steps

```bash
git clone <your-repository-url>
cd Sample-LMS-Python

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
```

---

## ▶ Running the Application

### Start Ollama

```bash
ollama serve
```

### Start FastAPI

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

```text
http://localhost:8000
```

---

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | localhost | Ollama server URL |
| `OLLAMA_MODEL` | mistral | LLM model |
| `DATABASE_URL` | SQLite | Database connection |
| `SECRET_KEY` | dev key | Session encryption |
| `SESSION_COOKIE_NAME` | lxp_session | Cookie name |

Generate secure secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🧪 Running Tests

```bash
pytest
pytest -v
pytest tests/test_ai_service.py -v
```

---

## ⚠ Known Limitations

- Ollama must be running for AI workflows
- External APIs require internet access
- SQLite is not ideal for production workloads
- No email verification
- Session auth only (JWT recommended for scale)

---

## 🚀 Future Enhancements

- JWT authentication
- PostgreSQL migration
- Role-based access control
- AI recommendations feedback loop
- Course completion analytics dashboard
- Azure OpenAI integration
- Multi-tenant support

---

## 📄 License

Add your preferred license here.

Example:

```text
MIT License
```

---

## 👨‍💻 Author

Developed as an AI-powered learning platform accelerator using FastAPI and local LLM orchestration.

---