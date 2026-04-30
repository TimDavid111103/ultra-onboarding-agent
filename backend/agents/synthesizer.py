import json
import anthropic

from models.schemas import StudentProfile
from constants.rubrics import DOWNSTREAM_RUBRICS

SYSTEM_PROMPT = """\
You are a student profiler for Ultra, a platform that routes high school students to the right \
downstream agents: Internship Match, College Chance, Entrepreneurship, and Research.

You will receive a student's parsed resume, the full transcript of their onboarding interview, \
and their GitHub activity. Your job is to synthesize what the CONVERSATION revealed — beyond \
what is already visible on the resume — into a structured profile that downstream agents can use.

━━━ GUIDING PRINCIPLE ━━━
The resume is already known. The interview is what you are synthesizing.
Subcategory context fields must draw from what the student SAID in the interview. \
Do not restate resume bullets. Surface depth, motivation, failures, self-awareness, \
specific details, and anything that enriches or complicates the resume picture.

━━━ CONFIDENCE SCORES (0–100) ━━━
Confidence scores reflect how much rubric-relevant evidence exists for the downstream agent to \
work with — NOT how much the conversation talked about a topic, and NOT a rating of the student.

Ask: "If the downstream agent applied its grading rubric right now, how much scoreable signal \
would it find?" Score based on how well the student's known information maps to each rubric criterion.

- 80–100: Strong rubric-relevant evidence present across the criteria this agent evaluates.
- 50–79: Partial evidence — some criteria are well-supported, others have gaps.
- 0–49: Little to no rubric-relevant evidence for this agent's criteria.

A student who explicitly said they have no entrepreneurial interest and no products should score \
near 0 for Venture Talent confidence — not because the topic was avoided, but because the rubric \
requires paying customers or MRR and none exist. A student with 1.5 years of formal lab work, \
a named PI, specific methodologies, and a pending co-authorship should score near 100 for \
Research Prior Experience — the rubric has exactly what it needs to evaluate them.

━━━ SUBCATEGORY CONTEXT ━━━
Each subcategory gets 2–4 sentences drawn from the conversation. Write in third person. \
Be specific — name actual things the student said (projects, reasoning, failures, habits). \
If a subcategory produced no conversation signal, say so explicitly in one sentence.

━━━ KEY POINTS ━━━
3–4 bullets per vertical of the most notable things the conversation revealed that a downstream \
agent would not know from the resume alone. These should be the most signal-rich facts.

━━━ SKILLS / GOALS / INTERESTS ━━━
Populate these from BOTH the resume and the conversation. The conversation should enrich these \
fields — add skills, interests, and goals that came up in discussion, not just what's listed.
"""

SYSTEM_PROMPT = SYSTEM_PROMPT + DOWNSTREAM_RUBRICS

_TOOL = {
    "name": "create_student_profile",
    "description": (
        "Synthesize a student profile from the interview conversation. "
        "Focus on what the conversation revealed beyond the resume."
    ),
    "input_schema": StudentProfile.model_json_schema(),
}


def synthesize_profile(
    resume_data: dict,
    conversation: list[dict],
    github_activity: dict | None = None,
) -> dict:
    client = anthropic.Anthropic()

    conversation_text = "\n".join(
        f"{'Student' if m['role'] == 'user' else 'Counselor'}: {m['content']}"
        for m in conversation
    )

    user_message = (
        f"RESUME DATA:\n{json.dumps(resume_data, indent=2)}\n\n"
        f"INTERVIEW TRANSCRIPT:\n{conversation_text}\n\n"
        f"GITHUB ACTIVITY:\n{json.dumps(github_activity, indent=2)}"
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=[_TOOL],
        tool_choice={"type": "tool", "name": "create_student_profile"},
        messages=[{"role": "user", "content": user_message}],
    )

    for block in response.content:
        if hasattr(block, "type") and block.type == "tool_use" and block.name == "create_student_profile":
            return StudentProfile(**block.input).model_dump()

    raise RuntimeError("Synthesizer did not return a student profile")
