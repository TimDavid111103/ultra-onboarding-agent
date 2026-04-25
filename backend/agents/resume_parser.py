import json
import anthropic

RESUME_TOOL = {
    "name": "extract_resume",
    "description": "Extract structured information from a student's resume text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Student's full name"},
            "graduation_year": {"type": ["integer", "null"], "description": "Expected high school graduation year"},
            "gpa": {"type": ["number", "null"], "description": "GPA (unweighted if available)"},
            "test_scores": {
                "type": "object",
                "properties": {
                    "SAT": {"type": ["integer", "null"]},
                    "ACT": {"type": ["integer", "null"]},
                },
                "required": ["SAT", "ACT"],
            },
            "courses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Notable courses (AP, IB, honors, college-level)",
            },
            "activities": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Extracurricular activities, clubs, sports, arts",
            },
            "work_experience": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Jobs, internships, volunteer work",
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Technical and soft skills listed",
            },
            "awards": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Awards, honors, recognitions",
            },
            "summary_detected": {
                "type": "string",
                "description": "Any personal statement or summary section found verbatim, or empty string",
            },
        },
        "required": [
            "name", "graduation_year", "gpa", "test_scores",
            "courses", "activities", "work_experience", "skills", "awards",
            "summary_detected",
        ],
    },
}

SYSTEM_PROMPT = (
    "You are a precise resume parser for a high school student opportunity platform. "
    "Extract all structured information from the resume text provided. "
    "If a field is not present, use null or an empty list as appropriate. "
    "Do not infer or hallucinate information not present in the text."
)


def parse_resume(resume_text: str) -> dict:
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=[RESUME_TOOL],
        tool_choice={"type": "tool", "name": "extract_resume"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Please extract all structured information from this resume:\n\n{resume_text}",
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_resume":
            return block.input

    raise RuntimeError("Resume parser did not return structured data")
