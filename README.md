# Ultra Onboarding Agent

A self-initiated project built around a problem observed on [useultra.ai](https://useultra.ai) — students need a fast, intelligent way to go from a resume to a rich, structured profile that Ultra can use to match them to the right opportunities.

## What it does

The agent conducts a conversational onboarding interview with a high school student, then synthesizes everything — resume, conversation, and GitHub activity — into a structured profile with rubric-based opportunity ratings across four areas: **College Admissions**, **Internships**, **Research**, and **Entrepreneurship**.

## How it fits into Ultra

Ultra matches students to opportunities. This agent solves the cold-start problem: getting enough signal on a new student to make those matches meaningful. The output profile is designed to feed directly into Ultra's matching layer.

---

## Architecture

Three Claude-powered agents run in sequence:

1. **Resume Parser** — extracts structured fields from a raw PDF or DOCX upload
2. **Interviewer** — conducts an 8–10 question SSE-streamed conversation to fill in what the resume misses
3. **Synthesizer** — combines resume data, conversation transcript, and GitHub activity into a rated student profile

---

## File Structure

```
ultra-onboarding-agent/
│
├── backend/
│   ├── main.py                          # FastAPI app; all endpoints wired here
│   ├── requirements.txt                 # Python dependencies
│   │
│   ├── agents/
│   │   ├── resume_parser.py             # Parses uploaded document into structured resume fields
│   │   ├── interviewer.py               # Streams interview turns; tracks 5-area coverage internally
│   │   └── synthesizer.py               # Produces rated student profile using tool-forced JSON output
│   │
│   ├── constants/
│   │   └── github_activity.py           # Default GitHub activity block used in live app (average student)
│   │
│   ├── models/
│   │   └── schemas.py                   # Session dataclass + shape comments for all major data types
│   │
│   ├── utils/
│   │   └── document_parser.py           # Extracts raw text from PDF and DOCX uploads
│   │
│   └── tests/
│       ├── run_synthesizer.py           # Eval runner: loads a profile and calls the synthesizer directly
│       └── profiles/                    # JSON test profiles; add one per student scenario you want to eval
│
└── frontend/
    ├── app/
    │   ├── layout.tsx                   # Root layout; loads Playfair Display + Geist Sans fonts
    │   ├── globals.css                  # Global styles; zinc-based dark theme, CSS variables
    │   ├── page.tsx                     # Landing page with resume upload flow
    │   ├── onboarding/page.tsx          # Interview page; renders ChatInterface component
    │   └── profile/[sessionId]/page.tsx # Profile results page; renders ProfileDisplay component
    │
    └── components/
        ├── ResumeUpload.tsx             # Drag-and-drop resume upload; kicks off a session
        ├── ChatInterface.tsx            # SSE-streamed chat UI; signals completion when interview is done
        └── ProfileDisplay.tsx           # Renders all four opportunity rating blocks with subcriteria
```

---

## Running locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Requires `backend/.env` with `ANTHROPIC_API_KEY=...`

**Running the synthesizer in isolation** (profile-based eval):
```bash
cd backend
python tests/run_synthesizer.py tests/profiles/my_profile.json
python tests/run_synthesizer.py tests/profiles/my_profile.json --ratings-only
```

---
