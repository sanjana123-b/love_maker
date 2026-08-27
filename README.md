# 💘 LoveMatch — Production-Grade Matchmaking Platform

A modern, high-performance, real-time matchmaking web application built with **Django 5.x**, **Django Channels (WebSockets)**, **PostgreSQL / Redis**, and **Google Gemini AI**. LoveMatch combines smart psychological compatibility scoring with an interactive Tinder-style swipe deck, multi-dimensional radar analytics, in-chat date planning, AI spark icebreakers, and a comprehensive Trust & Safety moderation subsystem.

---

## 🌟 Key Features

### 1. 🔍 Discovery & Matching Engine
- **Interactive Swipe Deck:** Touch and gesture-enabled card deck (Swipe Right to Like, Left to Pass, Up to Superlike) with celebratory match modals.
- **Multi-Dimensional Compatibility Radar:** 5-axis visual breakdown (Romance, Fun & Humor, Values, Lifestyle Pace, and Communication) powered by Chart.js.
- **Smart Category Quiz:** Psychological compatibility engine weighted across lifestyle, values, romance, and personality dimensions.
- **Astrological & Shared Interests Synergy:** Elemental zodiac harmony and tag-based overlap bonuses.

### 2. 💬 Real-Time Communication Suite
- **Live Bidirectional Chat:** WebSocket messaging via Django Channels & ASGI.
- **Live Typing Indicators & Read Receipts:** Double checkmark delivery tracking and active presence status.
- **✨ AI Spark Icebreaker Generator:** Contextual conversation starters powered by Google Gemini API & dynamic heuristic fallback.
- **💌 In-Chat Date Planner:** Propose, accept, or decline curated date ideas directly within conversations.

### 3. 🛡️ Trust, Safety & Profile Customization
- **Multi-Photo Gallery:** Support for up to 6 gallery photos with primary avatar selector.
- **Profile Prompts:** Customizable answer cards (*"My ideal first date...", "A non-negotiable for me is..."*).
- **Profile Strength Meter:** Gamified completeness indicator with actionable improvement tips.
- **Block & Report Shield:** Complete user blocking, instant unmatching, and structured report tickets for admin moderation.
- **Incognito / Ghost Mode:** Option to browse privately without appearing in public discovery decks.

---

## 🏗️ Architecture & Tech Stack

- **Backend:** Python 3.12 / 3.13, Django 5.x, Django Channels (ASGI), Daphne
- **Database:** PostgreSQL (Production) / SQLite (Local Dev)
- **Cache & Message Broker:** Redis 7 (WebSockets channel layer & caching)
- **AI Engine:** Google Gemini API (`gemini-2.5-flash` via `google-genai` SDK)
- **Frontend:** Bootstrap 5.3, Vanilla ES6 JavaScript, Chart.js, Canvas-Confetti, CSS3 animations
- **Testing:** `pytest`, `pytest-django`, `pytest-cov`
- **DevOps:** Docker, Docker Compose, GitHub Actions CI/CD, WhiteNoise

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.12+
- Git
- (Optional) Docker & Docker Compose

### 1. Local Setup

```bash
# Clone the repository
git clone https://github.com/sanjana123-b/love_maker.git
cd love_maker

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run database migrations and seed interest tags
python manage.py migrate
python manage.py seed_data

# Start Daphne ASGI Server
daphne -b 127.0.0.1 -p 8000 lovematch.asgi:application
```

Open `http://127.0.0.1:8000/` in your browser.

---

### 2. Docker Setup (Production Stack)

Run the full stack with PostgreSQL, Redis, and Daphne ASGI in one command:

```bash
docker-compose up --build -d
```

Access the application at `http://localhost:8000/`.

---

## 🧪 Running Automated Tests

Run the complete test suite:

```bash
pytest
```

Run tests with code coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DEBUG` | Enable/disable debug mode | `True` (Dev) / `False` (Prod) |
| `SECRET_KEY` | Django cryptographic secret key | (Required in Prod) |
| `DATABASE_URL` | Database connection string | `sqlite:///db.sqlite3` |
| `REDIS_URL` | Redis server URL for WebSockets | `redis://127.0.0.1:6379/0` |
| `GEMINI_API_KEY` | Google AI Studio API Key for smart icebreakers | (Optional) |
| `SECURE_SSL_REDIRECT` | Enforce HTTPS redirects in production | `False` |

---

## 🌿 Git Branches

- `main`: Production release branch
- `feature/phase-1-foundation-security-db`: Enterprise foundation, security config, environment decoupling, and database schema
- `feature/phase-2-matching-swipe-engine`: Interactive card swiping deck, multi-dimensional compatibility radar, date proposals
- `feature/phase-3-realtime-chat-ai`: Real-time WebSocket chat, typing indicators, AI spark icebreakers
- `feature/phase-4-safety-multiphoto-profile`: Trust & Safety block/report, multi-photo uploads, profile prompts, profile strength meter
- `feature/phase-5-docker-ci-tests`: Automated test suite, Docker containerization, and GitHub Actions CI/CD

---

## 📄 License & Credits

Developed with ❤️ for **LoveMatch**.
