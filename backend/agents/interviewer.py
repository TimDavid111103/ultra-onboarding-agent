import json
from typing import AsyncIterator
import anthropic

INTERVIEW_TOOL = {
    "name": "interview_turn",
    "description": (
        "Return your next message to the student along with updated coverage scores "
        "and whether the interview is complete."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Your conversational response / next question for the student.",
            },
            "coverage": {
                "type": "object",
                "description": "Coverage depth (0=not covered, 1=surface, 2=good, 3=deep) for each area.",
                "properties": {
                    "academics": {"type": "integer", "minimum": 0, "maximum": 3},
                    "extracurriculars": {"type": "integer", "minimum": 0, "maximum": 3},
                    "experience_and_projects": {"type": "integer", "minimum": 0, "maximum": 3},
                    "goals_and_interests": {"type": "integer", "minimum": 0, "maximum": 3},
                    "character_and_drive": {"type": "integer", "minimum": 0, "maximum": 3},
                },
                "required": [
                    "academics", "extracurriculars", "experience_and_projects",
                    "goals_and_interests", "character_and_drive",
                ],
            },
            "is_complete": {
                "type": "boolean",
                "description": (
                    "Set to true once ALL coverage areas are >= 2 AND you have asked "
                    "at least 8 questions AND you have said a warm closing message."
                ),
            },
        },
        "required": ["message", "coverage", "is_complete"],
    },
}

SYSTEM_TEMPLATE = """\
You are conducting a short intake interview for Ultra, a platform that routes students to \
the right opportunities: college admissions, internships, research, and entrepreneurship.

You have the student's resume:
<resume>
{resume_json}
</resume>

Your goal is to fill in what the resume doesn't show. You're not validating what's already \
there — you're digging for depth, motivation, failures, habits, and specifics that only \
come out in conversation.

You are gathering signal across four areas:
  1. COLLEGE ADMISSIONS — target schools and honest reasoning, academic context beyond stats, \
     extracurricular depth, intellectual interests, character
  2. INTERNSHIPS — what they've actually built, technical depth, real output and users, \
     work ethic and consistency
  3. RESEARCH — specific interests and knowledge, prior lab or project experience, \
     how deep they've gone and for how long
  4. ENTREPRENEURSHIP — anything they've built or tried to sell, actual traction, \
     how they think about problems and trade-offs

COVERAGE AREAS — get solid depth on all five before wrapping up:
  - academics: grades in context, course rigor, what they're genuinely good at
  - extracurriculars: what they actually do and how seriously
  - experience_and_projects: real technical or project work, output, who uses it
  - goals_and_interests: where they want to go and why, what they care about
  - character_and_drive: how they work, what drives them, how they handle hard things

INTERVIEW GUIDELINES:
- Talk like a normal person. Skip the affirmations ("That's great!", "Really interesting!").
- Ask one question at a time. Keep it conversational.
- React to what they say — follow up on anything that sounds interesting or worth probing.
- Don't re-ask what's obvious from the resume. Push past the surface.
- Aim for 8–10 exchanges total.
- After 8+ student responses with all areas at depth 2+, wrap up naturally and set is_complete = true.
- Never use asterisks (*) for emphasis. Never use em dashes (—). Write in plain prose.

ALWAYS respond using the interview_turn tool — never reply as plain text.
"""


async def stream_interview_turn(
    resume_data: dict,
    conversation: list[dict],
    current_coverage: dict,
) -> AsyncIterator[tuple[str, str]]:
    """
    Async generator that yields (event_type, data) tuples.
    event_type is "token", "meta", or "done".
    """
    client = anthropic.AsyncAnthropic()

    system = SYSTEM_TEMPLATE.format(resume_json=json.dumps(resume_data, indent=2))

    # Build messages: inject current coverage as a system note before the last user message
    messages = list(conversation)

    # Prepend coverage hint as a hidden system note via a user-prefixed assistant reminder
    question_count = sum(1 for m in conversation if m["role"] == "user")
    coverage_hint = (
        f"\n\n[Internal tracker — do not mention to student: "
        f"student responses so far={question_count}, "
        f"academics={current_coverage.get('academics', 0)}/2, "
        f"extracurriculars={current_coverage.get('extracurriculars', 0)}/2, "
        f"experience_and_projects={current_coverage.get('experience_and_projects', 0)}/2, "
        f"goals_and_interests={current_coverage.get('goals_and_interests', 0)}/2, "
        f"character_and_drive={current_coverage.get('character_and_drive', 0)}/2. "
        f"Signal is_complete=true after 8+ student responses with all areas >= 2.]"
    )
    if messages and messages[-1]["role"] == "user":
        messages = messages[:-1] + [
            {
                "role": "user",
                "content": messages[-1]["content"] + coverage_hint,
            }
        ]

    full_tool_json = ""
    in_tool_input = False

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        tools=[INTERVIEW_TOOL],
        tool_choice={"type": "tool", "name": "interview_turn"},
        messages=messages,
    ) as stream:
        async for event in stream:
            # Stream the "message" field characters as they arrive inside the tool input JSON
            if hasattr(event, "type"):
                if event.type == "content_block_start":
                    if hasattr(event, "content_block") and event.content_block.type == "tool_use":
                        in_tool_input = True
                        full_tool_json = ""

                elif event.type == "content_block_delta" and in_tool_input:
                    if hasattr(event.delta, "partial_json"):
                        chunk = event.delta.partial_json
                        full_tool_json += chunk
                        # Try to extract streamed characters from the "message" value
                        # We stream the raw partial JSON and let the frontend parse tokens
                        # from the "message" field incrementally by sending delta chunks.
                        yield ("token", chunk)

                elif event.type == "content_block_stop" and in_tool_input:
                    in_tool_input = False

    # Parse the completed tool input
    try:
        tool_data = json.loads(full_tool_json)
        meta = {
            "coverage": tool_data.get("coverage", current_coverage),
            "is_complete": tool_data.get("is_complete", False),
            "message": tool_data.get("message", ""),
        }
    except (json.JSONDecodeError, KeyError):
        meta = {
            "coverage": current_coverage,
            "is_complete": False,
            "message": "",
        }

    yield ("meta", json.dumps(meta))
    if meta["is_complete"]:
        yield ("done", "")
