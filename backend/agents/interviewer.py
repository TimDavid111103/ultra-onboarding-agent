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
                    "activities": {"type": "integer", "minimum": 0, "maximum": 3},
                    "goals": {"type": "integer", "minimum": 0, "maximum": 3},
                    "values": {"type": "integer", "minimum": 0, "maximum": 3},
                    "opportunity_fit": {"type": "integer", "minimum": 0, "maximum": 3},
                },
                "required": ["academics", "activities", "goals", "values", "opportunity_fit"],
            },
            "is_complete": {
                "type": "boolean",
                "description": (
                    "Set to true once ALL coverage areas are >= 1 AND you have asked "
                    "at least 3 questions AND you have said a warm closing message."
                ),
            },
        },
        "required": ["message", "coverage", "is_complete"],
    },
}

SYSTEM_TEMPLATE = """\
You are a warm, curious college counselor helping a high school student build their profile \
on Ultra, a platform that matches students to college opportunities, internships, research \
programs, and entrepreneurship resources.

You have already reviewed the student's resume:
<resume>
{resume_json}
</resume>

Your job is to conduct a friendly, conversational interview that uncovers information the \
resume doesn't capture — motivations, story, values, and specific interests across Ultra's \
four opportunity categories:
  1. College admissions (target schools, reach/match/safety thinking, essay themes)
  2. Internships (industries, roles, companies of interest)
  3. Research (academic fields, labs, professors, prior research)
  4. Entrepreneurship (ideas, projects, risk appetite, role models)

INTERVIEW GUIDELINES:
- Speak like a supportive mentor, not a form. Be warm, specific, and encouraging.
- Build on what the student just said before asking the next question.
- Ask ONE question at a time. Make it feel like a real conversation.
- Each question should touch on MULTIPLE coverage areas at once where natural — e.g. ask \
  about goals and values in the same question.
- Do not repeat topics already covered.
- Aim for 3–5 questions TOTAL then wrap up. This is a quick demo interview.
- After 3 substantive student responses, write a warm closing message and set is_complete = true \
  (all coverage areas will be at least 1 by then).

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
        f"academics={current_coverage['academics']}/1, "
        f"activities={current_coverage['activities']}/1, "
        f"goals={current_coverage['goals']}/1, "
        f"values={current_coverage['values']}/1, "
        f"opportunity_fit={current_coverage['opportunity_fit']}/1. "
        f"Signal is_complete=true after 3+ student responses with all areas >= 1.]"
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
