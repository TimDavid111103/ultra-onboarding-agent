# Ultra Onboarding Agent

A self-initiated project built for [useultra.ai](https://useultra.ai). Students need a fast, intelligent way to go from a resume to a rich profile that Ultra can act on. This agent does that in a single onboarding session.

---

## What It Does

The agent conducts a conversational interview with a high school student, then synthesizes the resume, conversation, and GitHub activity into a structured profile. That profile includes confidence scores and conversation-sourced context for each of Ultra's four downstream agents: College Chance, Internship Match, Research, and Entrepreneurship.

---

## How It Fits Into Ultra

Ultra routes students to opportunities. The bottleneck is signal: a resume alone isn't enough to make confident matches. This agent solves that by running a targeted intake interview and producing a profile that the downstream agents can evaluate immediately, without needing to ask the student anything again.

The confidence scores in the output reflect how much rubric-relevant evidence exists for each area, not how much the topic came up in conversation. A student with no products scores near zero on Venture Talent. A student with 18 months of formal lab work scores near 100 on Research Prior Experience.

---

## Architecture

Three Claude-powered agents run in sequence:

1. **Resume Parser** — extracts structured fields from a PDF or DOCX upload
2. **Interviewer** — runs an 8-10 question SSE-streamed conversation, tracking coverage across five areas internally
3. **Synthesizer** — combines resume, transcript, and GitHub activity into a rated profile using tool-forced structured output

---

## File Structure

```
ultra-onboarding-agent/
│
├── backend/
│   ├── main.py                          # FastAPI app and all endpoints
│   ├── requirements.txt
│   │
│   ├── agents/
│   │   ├── resume_parser.py             # Parses uploaded document into structured resume fields
│   │   ├── interviewer.py               # Streams interview turns; tracks 5-area coverage
│   │   └── synthesizer.py               # Produces rated student profile via Pydantic + tool use
│   │
│   ├── constants/
│   │   ├── rubrics.py                   # Downstream agent grading rubrics injected into synthesizer
│   │   └── github_activity.py           # Default GitHub activity block (average student baseline)
│   │
│   ├── models/
│   │   └── schemas.py                   # Session dataclass + Pydantic models for profile output
│   │
│   ├── utils/
│   │   └── document_parser.py           # Extracts raw text from PDF and DOCX uploads
│   │
│   └── tests/
│       ├── run_synthesizer.py           # Eval runner: loads a profile fixture and calls synthesizer
│       └── profiles/                    # JSON test fixtures; one per student scenario
│
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   ├── globals.css
    │   ├── page.tsx                     # Landing page with resume upload
    │   ├── onboarding/page.tsx          # Interview page
    │   └── profile/[sessionId]/page.tsx # Profile results page
    │
    └── components/
        ├── ResumeUpload.tsx             # Drag-and-drop upload; starts a session
        ├── ChatInterface.tsx            # Streaming chat UI; shows generate button on completion
        └── ProfileDisplay.tsx           # Renders confidence scores and context for all four verticals
```

---

## Running Locally

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

Requires `backend/.env` with `ANTHROPIC_API_KEY=sk-...`

**Test the synthesizer in isolation:**
```bash
cd backend
python tests/run_synthesizer.py tests/profiles/jason_park.json
python tests/run_synthesizer.py tests/profiles/jason_park.json --full
```
