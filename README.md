# 🧠 MeetingIQ

> AI-powered meeting intelligence. Upload a transcript, get a full structured report in seconds.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-orange)](https://groq.com)

---

## Overview

Most meetings produce a wall of notes nobody reads. MeetingIQ changes that — paste a transcript or upload an audio file, and nine AI tools run concurrently to extract every decision, action item, financial figure, risk, commitment, and open question. The result is a structured report you can read in two minutes, download as a PDF, and send to all attendees.

Unlike basic summarisers, MeetingIQ uses a 70B-parameter LLM to understand *semantic context* — not just keywords. It knows the difference between "we should look into this" and "Sarah owns this by Friday."

---

## Features

- **Multi-format input** — paste plain text, upload audio (MP3/MP4/WAV/M4A), PDF, DOCX, or TXT
- **Audio transcription** — Groq Whisper with speaker diarisation (`[Speaker 1]`, `[Speaker 2]`)
- **9 concurrent AI tools** — all run in parallel via `asyncio` + `ThreadPoolExecutor` for minimum latency
- **Structured extraction** — actions, decisions, financials, priorities, commitments, questions, people, dates, risks
- **Pydantic validation** — enum coercion handles freeform LLM output gracefully (no crashes on edge cases)
- **PDF report** — branded, dark-theme A4 report with cover page, stat summary, and section tables
- **PowerPoint export** — 16:9 slide deck with the same data, ready to present
- **Email delivery** — sends PDF + PPT to all attendees via Gmail SMTP
- **Meeting archive** — every report persisted in PostgreSQL (prod) or SQLite (local dev)
- **Eval framework** — automated test suite scoring action recall, decision recall, and meeting type accuracy across 10 synthetic transcripts

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  Streamlit UI   │────▶│  FastAPI Backend  │────▶│  Groq API            │
│  frontend/app.py│     │  main.py          │     │  llama-3.3-70b       │
└─────────────────┘     └──────────────────┘     │  whisper-large-v3    │
                                │                 └──────────┬───────────┘
                                │                            │
                         ┌──────▼──────────────────────────▼──────────┐
                         │           agent/runner.py                    │
                         │   9 tools run concurrently via asyncio       │
                         │   Core Summary · Actions · Financials        │
                         │   Priorities · Commitments · Questions       │
                         │   People · Dates · Risks                     │
                         └──────────────────────┬──────────────────────┘
                                                │
                              ┌─────────────────▼──────────────────┐
                              │  PostgreSQL (prod) / SQLite (local) │
                              │  PDF + PPTX export via ReportLab    │
                              │  Email via Gmail SMTP               │
                              └─────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Multi-page UI, session state, animated dark theme |
| Backend | FastAPI | REST API, file upload, rate limiting via SlowAPI |
| LLM | Groq — llama-3.3-70b-versatile | Semantic analysis, structured JSON extraction |
| Transcription | Groq — whisper-large-v3 | Audio → diarised transcript |
| Validation | Pydantic v2 | Schema enforcement, enum coercion for LLM output |
| Database | PostgreSQL (prod) / SQLite (local) | Report persistence across server restarts |
| ORM | SQLAlchemy | Models, queries, session management |
| PDF | ReportLab | Branded A4 report with cover page and tables |
| PPTX | python-pptx | 16:9 slide deck matching PDF design |
| Email | Gmail SMTP | Report delivery with PDF + PPT attachments |
| Eval | Custom framework | Automated scoring across 10 test transcripts |

---

## Project Structure

```
MeetingIQ/
├── main.py                      # FastAPI app — endpoints, rate limiting, file handling
├── database.py                  # SQLAlchemy models, init_db, save/fetch reports
├── agent/
│   ├── runner.py                # Async orchestrator — runs all 9 tools concurrently
│   └── tools.py                 # 9 extraction functions, Groq calls, retry logic
├── models/
│   └── schemas.py               # Pydantic models — FullReport, ActionItem, RiskItem etc.
├── services/
│   ├── parser.py                # File → text: audio transcription, PDF/DOCX/TXT extraction
│   ├── pdf_generator.py         # ReportLab PDF builder
│   ├── ppt_generator.py         # python-pptx slide deck builder
│   └── email_sender.py          # Gmail SMTP sender, email body builder
├── frontend/
│   └── app.py                   # Streamlit UI — upload, dashboard, history, send tabs
├── eval/
│   ├── ground_truth.py          # 10 annotated test transcripts with expected outputs
│   └── run_eval.py              # Eval runner — scores action recall, decisions, meeting type
├── .env.example
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- A free [Groq API key](https://console.groq.com)
- (Optional) Gmail account with an [App Password](https://support.google.com/accounts/answer/185833) for email delivery
- (Optional) ffmpeg for audio files over 25MB: `brew install ffmpeg`

### 1. Clone the repo

```bash
git clone https://github.com/Bhumi-dubey-16/MeetingIQ.git
cd MeetingIQ
```

### 2. Create a virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
GROQ_API_KEY=your_groq_key_here
DATABASE_URL=                    # leave blank to use local SQLite
GMAIL_SENDER=you@gmail.com       # optional — for email delivery
GMAIL_APP_PASSWORD=your_app_pw   # optional — Gmail App Password, not your login password
```

> If `DATABASE_URL` is not set, the app creates a local `meetingiq.db` SQLite file automatically. No database setup required.

### 5. Run the backend

```bash
uvicorn main:app --reload
```

API available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### 6. Run the frontend

```bash
streamlit run frontend/app.py
```

UI available at `http://localhost:8501`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyse` | Upload file or paste text, returns full report + report_id |
| `GET` | `/report/{id}` | Fetch a stored report by ID |
| `GET` | `/reports` | List recent reports (default: 20) |
| `GET` | `/download/pdf/{id}` | Download PDF for a report |
| `GET` | `/download/ppt/{id}` | Download PPTX for a report |
| `POST` | `/send-email` | Email PDF + PPTX to a list of recipients |

Rate limits: 5 analyses/minute, 10 downloads/minute, 3 emails/minute.

---

## The 9 Extraction Tools

Each tool is an independent function that calls the LLM with a targeted prompt and returns a typed Pydantic model. All 9 run concurrently; if one fails (e.g. rate limit), it falls back to an empty list so the rest of the report is never lost.

| # | Tool | Extracts |
|---|---|---|
| 1 | Core Summary | One-line summary, decisions made, next steps, meeting type |
| 2 | Action Items | Owner, task, deadline, priority (HIGH/MEDIUM/LOW) |
| 3 | Financial Items | Amounts, context, status, owner |
| 4 | Priorities | Urgency-flagged items grouped by level |
| 5 | Commitments | Person, what they committed to, target metric, deadline |
| 6 | Unresolved Questions | Open questions with context and who raised them |
| 7 | People & Roles | All attendees and referenced parties with role and email |
| 8 | Dates & Deadlines | Every date or timeframe mentioned with priority |
| 9 | Risks & Blockers | Risks with severity, owner, and any mitigation discussed |

---

## Eval Framework

MeetingIQ ships with an automated evaluation suite across 10 synthetic transcripts covering different meeting types: product planning, sales call, engineering standup, HR review, investor update, vendor negotiation, sprint retrospective, client onboarding, budget review, and incident response.

Each transcript has annotated ground truth — expected action item owners, expected decision keywords, and expected meeting type classification.

```bash
# Run all 10 cases
python -m eval.run_eval

# Run a single case
python -m eval.run_eval --id 01

# Verbose output (shows exactly what was missed)
python -m eval.run_eval --verbose

# Point at a different server
python -m eval.run_eval --url http://your-server.com
```

### Baseline results (free Groq tier)

| Case | Type | Actions | Decisions | Pass |
|---|---|---|---|---|
| 01 Product Planning | planning | 100% | 100% | ✅ |
| 02 Sales Call | sales | 100% | 100% | ✅ |
| 03 Engineering Standup | standup | 100% | 100% | ✅ |
| 04 HR Review | review | 100% | 67% | ✅ |
| 05 Investor Update | investor | 100% | 100% | ❌ type mismatch |
| 06 Vendor Negotiation | negotiation | 100% | 67% | ✅ |
| 07 Sprint Retro | retrospective | 100% | 67% | ✅ |
| 08 Client Onboarding | onboarding | 100% | 100% | ✅ |
| 09 Budget Review | budget | 100% | 100% | ✅ |
| 10 Incident Response | incident | 100% | 100% | ✅ |

**9/10 passing · 100% action recall across all cases**

> Note: these transcripts are synthetic and were designed by the same author as the extraction prompts. Real-world performance on unseen transcripts will differ — this suite validates that the pipeline is wired correctly, not that it generalises perfectly.

---

## Deployment

The app is ready to deploy on [Render](https://render.com).

1. Push your repo to GitHub
2. On Render: **New → PostgreSQL** → create a free database → copy the Internal Database URL
3. **New → Web Service** → connect your GitHub repo

**Backend service settings:**

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

**Frontend service settings:**

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0` |

**Environment variables:**

| Key | Value |
|---|---|
| `GROQ_API_KEY` | Your key from console.groq.com |
| `DATABASE_URL` | Internal PostgreSQL URL from Render |
| `GMAIL_SENDER` | Your Gmail address (optional) |
| `GMAIL_APP_PASSWORD` | Gmail App Password (optional) |

---

## Known Limitations

- **Latency** — 9 parallel LLM calls take 15–25s on the free Groq tier. Rate limit errors trigger automatic retry with exponential backoff (15s, 30s, 45s). Upgrading to a paid tier or caching repeated transcripts would bring this under 5s.
- **Eval coverage** — the current test suite uses synthetic transcripts. A production eval would require real meeting data with human-labelled ground truth.
- **Audio diarisation** — speaker labels are best-effort. Groq Whisper returns segment-level speaker IDs but accuracy drops with overlapping speech or heavy accents.
- **Large audio files** — files over 25MB are split into 10-minute chunks via ffmpeg. Speaker numbering is offset per chunk to avoid collisions but may not perfectly track the same person across chunk boundaries.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | — | API key from console.groq.com |
| `DATABASE_URL` | No | SQLite fallback | PostgreSQL connection string |
| `GMAIL_SENDER` | No | — | Gmail address for email delivery |
| `GMAIL_APP_PASSWORD` | No | — | Gmail App Password (not your login password) |

---

## License

MIT