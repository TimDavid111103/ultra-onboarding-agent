import json
import uuid
from pathlib import Path
from typing import AsyncIterator

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from constants.github_activity import DEFAULT_GITHUB_ACTIVITY
from agents.interviewer import stream_interview_turn
from agents.resume_parser import parse_resume
from agents.synthesizer import synthesize_profile
from models.schemas import Session
from utils.document_parser import extract_text

app = FastAPI(title="Ultra Onboarding Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict[str, Session] = {}


# ---------- Upload resume ----------

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.lower().endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(400, "Only PDF or DOCX files are supported.")

    raw_bytes = await file.read()
    try:
        text = extract_text(raw_bytes, filename)
    except ValueError as e:
        raise HTTPException(400, str(e))

    if not text.strip():
        raise HTTPException(400, "Could not extract text from the uploaded file.")

    resume_data = parse_resume(text)
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(session_id=session_id, resume_data=resume_data)

    return {"session_id": session_id, "resume_data": resume_data}


# ---------- Demo session (Jason Park skip) ----------

@app.post("/api/session/demo")
async def load_demo_session():
    fixture_path = Path(__file__).parent / "tests" / "profiles" / "jason_park.json"
    data = json.loads(fixture_path.read_text())

    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(
        session_id=session_id,
        resume_data=data["resume_data"],
        conversation=data["conversation"],
        is_complete=True,
        coverage={k: 3 for k in [
            "academics", "extracurriculars", "experience_and_projects",
            "goals_and_interests", "character_and_drive",
        ]},
    )

    return {"session_id": session_id, "conversation": data["conversation"]}


# ---------- Interview message (SSE streaming) ----------

class MessageRequest(BaseModel):
    content: str


async def _sse_interview_stream(session: Session, user_message: str) -> AsyncIterator[str]:
    session.conversation.append({"role": "user", "content": user_message})

    full_message = ""
    meta_payload: dict = {}

    async for event_type, data in stream_interview_turn(
        session.resume_data, session.conversation, session.coverage
    ):
        if event_type == "token":
            yield f"data: {json.dumps({'type': 'token', 'chunk': data})}\n\n"
        elif event_type == "meta":
            meta_payload = json.loads(data)
            full_message = meta_payload.get("message", "")
            session.coverage = meta_payload.get("coverage", session.coverage)
            session.is_complete = meta_payload.get("is_complete", False)
            yield f"event: meta\ndata: {data}\n\n"
        elif event_type == "done":
            yield "event: done\ndata: {}\n\n"

    if full_message:
        session.conversation.append({"role": "assistant", "content": full_message})


@app.post("/api/session/{session_id}/message")
async def send_message(session_id: str, body: MessageRequest):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    if session.is_complete:
        raise HTTPException(400, "Interview is already complete. Generate your profile.")

    return StreamingResponse(
        _sse_interview_stream(session, body.content),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------- Synthesize profile ----------

@app.post("/api/session/{session_id}/synthesize")
async def synthesize(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    if not session.conversation:
        raise HTTPException(400, "No interview conversation found. Complete the interview first.")

    profile = synthesize_profile(session.resume_data, session.conversation, DEFAULT_GITHUB_ACTIVITY)
    session.profile = profile
    return profile


# ---------- Get profile ----------

@app.get("/api/session/{session_id}/profile")
async def get_profile(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    if not session.profile:
        raise HTTPException(404, "Profile not yet generated. Call /synthesize first.")
    return session.profile


# ---------- Health ----------

@app.get("/health")
async def health():
    return {"status": "ok"}
