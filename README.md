# CodeReview Memory Agent

> **AI Agents That Learn Using Hindsight** — A Hackathon Prototype

An intelligent, team-aware AI code review agent designed to learn development team standards, conventions, past mistakes, and architectural preferences over time using **real Hindsight memory** and **Groq LLM inference**.

---

## ⚠️ Phase 1 Status & Disclaimer

> **Current Status: Phase 1 (Foundation & Connectivity)**  
> Real Hindsight memory operations (retain/recall) and Groq LLM code review pipelines are **NOT** active yet. Phase 1 establishes the clean backend service skeletons, Pydantic data schemas, FastAPI endpoints, React dashboard, and client-server health handshake.

---

## 📖 Problem Statement

Standard AI code review tools treat every review in isolation. They repeatedly flag false positives or miss team-specific architectural patterns, naming conventions, and shared library rules.

**CodeReview Memory Agent** solves this by maintaining a long-term, adaptive memory of team conventions using Hindsight. Over time:
1. Developer submits code.
2. Hindsight recalls relevant team knowledge and prior feedback.
3. Groq LLM performs an ultra-fast, team-grounded code review.
4. Developers provide feedback or corrections.
5. Hindsight retains new learnings, improving all future reviews.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Data Validation**: Pydantic v2
- **Server**: Uvicorn
- **Testing**: Pytest + HTTPX

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: JavaScript (ESModules)
- **Styling**: Vanilla CSS (Modern Dark Developer UI)

### Future AI & Memory (Phase 2)
- **LLM Engine**: Groq (Llama 3.3 70B Versatile)
- **Memory Service**: Hindsight (Vectorize / Hindsight Cloud API)

---

## 📂 Project Structure

```text
CodeReview-Memory-Agent/
│
├── backend/
│   ├── main.py                  # FastAPI entry point & CORS configuration
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment configuration template
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── hindsight_service.py # Hindsight memory integration skeleton
│   │   └── llm_service.py       # Groq review integration skeleton
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── health.py            # GET /health endpoint
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic schemas (ReviewRequest, FeedbackRequest, etc.)
│   │
│   └── tests/
│       ├── __init__.py
│       └── test_health.py       # Pytest suite for API connectivity
│
├── frontend/
│   ├── package.json             # Frontend dependencies and scripts
│   ├── vite.config.js           # Vite dev server configuration
│   ├── index.html               # Web application entry page
│   │
│   └── src/
│       ├── main.jsx             # React DOM root mounting
│       ├── App.jsx              # Main dashboard component
│       ├── App.css              # Dashboard component styles
│       ├── index.css            # Design tokens and theme styling
│       ├── components/
│       │   └── HealthCard.jsx   # Live backend connectivity check card
│       └── services/
│           └── api.js           # Fetch client for backend API
│
├── .gitignore                   # Git ignore for Python venv, node_modules, .env
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### 1. Backend Setup

From the project root:

```bash
# Navigate to backend or stay in root and use backend's virtual environment
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

Verify backend health directly:
```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

API Documentation is available at `http://localhost:8000/docs`.

### 2. Frontend Setup

In a new terminal window:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

Open `http://localhost:5173` in your browser. Click **"Check Backend"** to verify real-time connectivity between React and FastAPI.

---

## 🧪 Running Tests

To run the automated backend test suite:

```bash
# From the backend directory with active virtual environment:
pytest
```

---

## 🗺️ Roadmap: Phase 2 Plan

In Phase 2, we will implement:
1. **Hindsight Memory Integration**:
   - Connection to Hindsight Cloud API.
   - Retain team preferences and rules into memory banks.
   - Recall relevant memories based on AST / code context matching.
2. **Groq Code Review Engine**:
   - High-throughput code review prompts with memory augmentation.
   - Structured JSON output with line-level suggestions.
3. **Feedback Loop Pipeline**:
   - Extraction of new team knowledge from developer acceptance/corrections.
   - Auto-updating Hindsight memory.
4. **Interactive Review Dashboard**:
   - Code editor / diff viewer in React with memory badges and feedback controls.
