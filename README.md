# 📈 Stock AI

> AI-powered stock analysis web app — search any stock, get technical indicators and an AI-generated summary, with per-user daily search limits and secure auth.

<p align="center">
  <strong>🔗 Live demo: <a href="https://stockai-tyagi-frontend.onrender.com">stockai-tyagi-frontend.onrender.com</a></strong><br>
  <sub>Hosted on Render's free tier — the first request after idle may take ~50s to wake.</sub>
</p>

<p align="center">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white">
</p>

---

## ✨ Features

- 🔎 **Stock analysis** — search any ticker and get price action, technical indicators, and momentum signals (data via Yahoo Finance, no paid API key required).
- 🤖 **AI insights** — an OpenAI-generated, plain-English summary of each stock's outlook.
- 🔐 **Secure auth** — email + password with email-OTP verification **and** Google OAuth (Sign in with Google), JWT access/refresh tokens.
- ⏱️ **Daily search limits** — per-user quotas tracked in the database, enforced with API rate limiting.
- 🗂️ **Today's searches** — history of what each user looked up.
- 🛡️ **Production hardening** — nginx reverse proxy with TLS, security headers, gzip, and tiered rate limits.

---

## 🏗️ Architecture

```
                        ┌────────────────────────┐
   Browser  ──HTTPS──▶  │  nginx (TLS, rate-limit)│
                        └───────────┬─────────────┘
                        ┌───────────┴─────────────┐
                        ▼                          ▼
              ┌──────────────────┐      ┌────────────────────┐
              │ Frontend (React) │      │ Backend (FastAPI)  │
              │ Vite + Tailwind  │      │  /api/v1/*         │
              └──────────────────┘      └─────────┬──────────┘
                                          ┌────────┴────────┐
                                          ▼                 ▼
                                 ┌────────────────┐  ┌────────────┐
                                 │ PostgreSQL 15  │  │  Redis 7   │
                                 │ (async + Alembic)│ │ (cache)    │
                                 └────────────────┘  └────────────┘
                                          │
                                          ▼
                              Yahoo Finance · OpenAI
```

## 🧰 Tech stack

| Layer | Tech |
|-------|------|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, React Router, Axios |
| **Backend** | FastAPI, Python 3.11, async SQLAlchemy, Alembic, Pydantic |
| **Data / AI** | Yahoo Finance (`yfinance`), OpenAI |
| **Storage** | PostgreSQL 15, Redis 7 |
| **Infra** | Docker / Docker Compose, nginx, Let's Encrypt |
| **Deploy** | Render (free) · Oracle Cloud / EC2 (Docker Compose) |

---

## 📁 Project structure

```
StockAI/
├── backend/                  # FastAPI app
│   ├── app/
│   │   ├── api/endpoints/     # auth + search/analyze routes
│   │   ├── core/             # config, security, rate limiting
│   │   ├── db/               # async SQLAlchemy session
│   │   └── services/         # stock data, AI, search limits
│   └── alembic/              # database migrations
├── frontend-react/           # React + Vite SPA
│   └── src/{pages,components,services}
├── nginx/                    # reverse-proxy config (domain-templated)
├── scripts/                  # deploy / dev / debug helpers
├── docker-compose.yml        # local development
├── docker-compose.prod.yml   # production stack
├── render.yaml               # Render Blueprint (one-click deploy)
└── DEPLOY.md                 # full deployment runbook
```

---

## 🚀 Run locally

**Prerequisites:** Docker + Docker Compose.

```bash
git clone https://github.com/tyagi-sam/StockAI.git
cd StockAI
cp env.example .env          # then fill in the values (see below)
./scripts/dev/start.sh       # builds & starts all services
```

Then open:
- Frontend → http://localhost:3000
- API docs → http://localhost:8000/docs

### Required environment variables
Copy `env.example` to `.env` and set at least:

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET` | session signing (≥ 32 chars) |
| `FERNET_KEY` | encrypts sensitive data (base64 32-byte key) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth login |
| `OPENAI_API_KEY` | AI summaries (optional) |
| `SMTP_*`, `FROM_*` | email OTP delivery |

> Full list and generation tips are in [`env.example`](env.example).

---

## ☁️ Deployment

This repo ships two paths, both documented in **[`DEPLOY.md`](DEPLOY.md)**:

1. **Render** (free, fastest) — via the included [`render.yaml`](render.yaml) Blueprint. Managed Postgres + Redis + backend + static frontend, no server to manage.
2. **Self-hosted VM** (Oracle Cloud Always Free / EC2) — `docker-compose.prod.yml` + nginx + Let's Encrypt. The public hostname is a single `DOMAIN` env var.

---

## 📌 Notes

- Stock data comes from **Yahoo Finance** (no paid key). A Zerodha integration exists in the codebase but is inactive, kept for a possible future feature.
- This is a personal/portfolio project for low-traffic use; the live demo runs on free-tier infrastructure that sleeps when idle.
