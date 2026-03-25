<div align="center">

# 🚀 API Gen Platform

**AI-Powered API Discovery & REST API Generator**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Discover the best APIs for your app idea, auto-generate REST APIs from Python code, deploy anywhere — all from a single platform.

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **API Discovery** | Describe your app idea and get ranked API recommendations from a curated catalog of 100+ APIs across 15 categories |
| 🤖 **AI Agent Mode** | Intelligent pipeline that discovers, verifies, ranks, and generates integration code — works with or without an LLM key |
| 🔬 **Code Analyzer** | Upload Python source files and get detailed analysis: functions, classes, type hints, async detection, ML/DB model detection |
| ⚡ **REST API Generator** | Auto-generate complete REST APIs in **FastAPI**, **Express**, **Express (TS)**, **Spring Boot**, **Gin (Go)**, or **ASP.NET** |
| 📄 **OpenAPI Spec** | Automatically generates an OpenAPI 3.0 specification for every generated project |
| 🌐 **API Gateway** | Generates rate-limiting, auth, and CORS middleware for your generated API |
| 📦 **Deployment Configs** | One-click generation of **Docker**, **Kubernetes**, **AWS Lambda**, **Vercel**, **Railway**, and **Render** configs |
| 🚀 **CI/CD Pipelines** | Generate production-ready **GitHub Actions** or **GitLab CI** pipelines with Docker and cloud deploy steps |
| 🐙 **GitHub Integration** | Push generated projects directly to GitHub and auto-configure repository secrets |
| 💻 **CLI Tool** | Full command-line interface: `scan`, `recommend`, and `deploy` commands |
| 🖥️ **Web UI** | Beautiful single-page frontend with tabs for Discovery, Generator, and Deploy |

---

## 🏗️ Architecture

```
API Gen Platform
├── main.py                  # FastAPI application entry point
├── config.py                # Central configuration (paths, DB, scoring weights)
├── database.py              # SQLAlchemy engine & session (SQLite)
├── models.py                # ORM models (APIEntry, APICategory, HealthCheck, …)
├── schemas.py               # Pydantic request/response schemas
│
├── discovery/               # API Discovery Engine
│   ├── engine.py            #   NLP-based idea → feature → API matching
│   ├── knowledge_base.py    #   Curated catalog of 100+ APIs (seeds the DB)
│   ├── ranking.py           #   Composite scoring (popularity, docs, reliability, …)
│   └── verifier.py          #   Live health checks via async HTTP
│
├── generator/               # REST API Code Generator
│   ├── analyzer.py          #   Python AST analysis (functions, classes, types)
│   ├── rest_generator.py    #   Multi-framework code generation
│   ├── framework_selector.py#   Auto-detect best framework for a project
│   └── doc_generator.py     #   OpenAPI spec & example request generation
│
├── agent/                   # AI Agent
│   └── ai_agent.py          #   Orchestrates discover → verify → rank → integrate
│
├── deployment/              # Deployment & CI/CD
│   ├── generators.py        #   Docker, K8s, AWS Lambda, Vercel, Railway, Render configs
│   ├── cicd.py              #   GitHub Actions / GitLab CI pipeline generation
│   └── github_integrator.py #   Push to GitHub & set secrets via PyGithub
│
├── gateway/                 # API Gateway Middleware
│   └── gateway_gen.py       #   Rate-limit, auth, CORS middleware generation
│
├── routes/                  # FastAPI Routers
│   ├── discovery.py         #   /api/discover, /api/apis, /api/verify, …
│   ├── generator.py         #   /api/generate, /api/analyze, /api/push-to-github, …
│   └── agent.py             #   /api/agent
│
├── cli/                     # Command-Line Interface
│   └── main.py              #   Click-based CLI (scan, recommend, deploy)
│
├── frontend/                # Web UI (vanilla HTML/CSS/JS)
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── data/                    # SQLite database
│   └── api_platform.db
│
└── generated_projects/      # Output directory for generated APIs
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- *(Optional)* `OPENAI_API_KEY` environment variable for enhanced AI Agent reasoning

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/api-gen.git
cd api-gen

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
python main.py
```

The server starts at **http://localhost:8000** with:

| URL | Description |
|---|---|
| `http://localhost:8000` | Web UI |
| `http://localhost:8000/docs` | Swagger / OpenAPI UI |
| `http://localhost:8000/redoc` | ReDoc documentation |
| `http://localhost:8000/health` | Health check |

---

## 📡 API Reference

### Discovery

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/discover` | Discover APIs for an app idea |
| `GET` | `/api/apis` | Browse the API catalog (filter, search, sort) |
| `GET` | `/api/apis/{slug}` | Detailed info for a specific API |
| `POST` | `/api/verify/{slug}` | Run a live health check on an API |
| `GET` | `/api/categories` | List all API categories with counts |
| `GET` | `/api/ranking/{slug}` | Get detailed scoring breakdown |

### Generator

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Analyze Python code (no generation) |
| `POST` | `/api/generate` | Generate a full REST API from Python code |
| `GET` | `/api/generate/{id}` | Retrieve a previously generated project |
| `GET` | `/api/projects` | List all generated projects |
| `POST` | `/api/generate-pipeline` | Generate a CI/CD pipeline config |
| `POST` | `/api/push-to-github` | Push a project to GitHub |

### Agent

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/agent` | AI Agent — discover, verify, rank and integrate |

### Settings

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/settings/github` | Get saved GitHub credentials |
| `POST` | `/api/settings/github` | Update GitHub credentials |

---

## 💻 CLI Usage

```bash
# Scan a Python project and generate a REST API
python cli/main.py scan ./my_project --framework fastapi --output ./generated

# Get API recommendations for an idea
python cli/main.py recommend "I want to build a travel planner app" --free-only

# Generate deployment configs
python cli/main.py deploy --project-name my-api --output ./deploy
```

---

## ⚙️ Configuration

All settings are managed via **environment variables** or `config.py`:

| Variable | Default | Description |
|---|---|---|
| `API_GEN_HOST` | `0.0.0.0` | Server bind address |
| `API_GEN_PORT` | `8000` | Server port |
| `API_GEN_DEBUG` | `true` | Enable hot-reload |
| `OPENAI_API_KEY` | *(empty)* | OpenAI key for enhanced AI Agent |
| `LLM_MODEL` | `gpt-4` | LLM model name |

### Scoring Weights

API recommendations are ranked by a **composite score** using configurable weights:

| Dimension | Weight |
|---|---|
| Popularity | 30% |
| Documentation | 20% |
| Reliability | 20% |
| Pricing | 15% |
| Latency | 15% |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn |
| Database | SQLite via SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| HTTP Client | httpx, aiohttp |
| CLI | Click, Rich |
| Templates | Jinja2 |
| GitHub | PyGithub, PyNaCl |
| Frontend | Vanilla HTML / CSS / JS |

---

## 🗄️ Database Models

| Model | Purpose |
|---|---|
| `APICategory` | Groups APIs into categories (e.g., Payments, Maps, AI) |
| `APIEntry` | Individual API with metadata, scoring, and health status |
| `HealthCheck` | Historical health-check results per API |
| `GeneratedProject` | Stores generated code, specs, and deployment configs |
| `UserSettings` | Persisted GitHub credentials |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <b>Built with ❤️ by the API Gen team</b>
</div>
