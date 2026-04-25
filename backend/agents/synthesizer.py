import json
import anthropic

PROFILE_TOOL = {
    "name": "create_student_profile",
    "description": (
        "Create a structured student profile from resume data and interview conversation. "
        "Includes retained profile fields and rubric-based opportunity ratings across four areas."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "academic": {
                "type": "object",
                "properties": {
                    "gpa": {"type": ["number", "null"]},
                    "test_scores": {
                        "type": "object",
                        "properties": {
                            "SAT": {"type": ["integer", "null"]},
                            "ACT": {"type": ["integer", "null"]},
                        },
                        "required": ["SAT", "ACT"],
                    },
                    "courses": {"type": "array", "items": {"type": "string"}},
                    "graduation_year": {"type": ["integer", "null"]},
                },
                "required": ["gpa", "test_scores", "courses", "graduation_year"],
            },
            "skills": {
                "type": "object",
                "properties": {
                    "technical": {"type": "array", "items": {"type": "string"}},
                    "soft": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["technical", "soft"],
            },
            "interests": {"type": "array", "items": {"type": "string"}},
            "goals": {
                "type": "object",
                "properties": {
                    "college_targets": {"type": "array", "items": {"type": "string"}},
                    "career_direction": {"type": "string"},
                    "research_interests": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["college_targets", "career_direction", "research_interests"],
            },
            "experience": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "org": {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": ["title", "org", "description"],
                },
            },
            "opportunity_ratings": {
                "type": "object",
                "description": (
                    "Rubric-based ratings across four opportunity areas. "
                    "Rating scale: 1 = Tier 1 (strongest), 5 = Tier 5 (weakest). "
                    "Be honest — these guide the student's development, not flatter them."
                ),
                "properties": {
                    "internship_match": {
                        "type": "object",
                        "description": (
                            "Tier is determined by external validation and demonstrated output. "
                            "Shipping something real that others use or engage with is the primary signal."
                        ),
                        "properties": {
                            "skills_and_talent": {
                                "type": "object",
                                "description": (
                                    "Technical stack depth, algorithmic aptitude, competition wins, "
                                    "external validation. Tier 1: national competition wins + high-visibility "
                                    "open source. Tier 2: strong stack + some external validation. "
                                    "Tier 3: solid skills but no competitive wins or community traction. "
                                    "Tier 4: developing skills, limited portfolio. Tier 5: minimal technical evidence."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "development_experience": {
                                "type": "object",
                                "description": (
                                    "Project complexity, code quality, repo health (stars, forks, docs, tests). "
                                    "Tier 1: production systems with real users, strong code quality. "
                                    "Tier 2: complex projects, some community engagement. "
                                    "Tier 3: well-architected personal projects, zero stars/forks. "
                                    "Tier 4: basic projects, limited complexity. Tier 5: minimal project evidence."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "work_ethic_and_output": {
                                "type": "object",
                                "description": (
                                    "GitHub contribution frequency, monthly distribution, sustained effort. "
                                    "Tier 1: consistent daily activity, no dips, thorough documentation. "
                                    "Tier 2: steady monthly contributions, minor dips. "
                                    "Tier 3: active but notable dips or sparse months. "
                                    "Tier 4: inconsistent, many gaps. Tier 5: minimal contribution history."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "overall_tier": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": "Holistic internship match tier considering all three criteria.",
                            },
                            "priority_actions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "2-4 concrete, specific actions to move up to the next tier.",
                            },
                        },
                        "required": [
                            "skills_and_talent", "development_experience", "work_ethic_and_output",
                            "overall_tier", "priority_actions",
                        ],
                    },
                    "college_chance": {
                        "type": "object",
                        "description": (
                            "Overall score is NOT an average — it weights strengths and ignores athletics "
                            "if not strong. Score 1 = all Harvard admits. Over 50% of Score 2s admitted to Harvard."
                        ),
                        "properties": {
                            "academic": {
                                "type": "object",
                                "description": (
                                    "GPA, test scores, class rank, coursework rigor. "
                                    "Score 1: top 1% nationally, near-perfect GPA/scores, explicit class rank. "
                                    "Score 2: strong GPA/scores with class rank provided. "
                                    "Score 3: strong GPA/scores but missing rank or course detail. "
                                    "Score 4: below-competitive stats. Score 5: significantly below range."
                                ),
                                "properties": {
                                    "score": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["score", "rationale"],
                            },
                            "extracurriculars": {
                                "type": "object",
                                "description": (
                                    "Leadership roles, measurable impact, scale of recognition. "
                                    "Score 1: national recognition, major leadership, published or awarded. "
                                    "Score 2: regional recognition or significant school leadership. "
                                    "Score 3: strong projects but no leadership, no external recognition. "
                                    "Score 4: limited activities. Score 5: no notable extracurriculars."
                                ),
                                "properties": {
                                    "score": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["score", "rationale"],
                            },
                            "mind": {
                                "type": "object",
                                "description": (
                                    "Scholarly curiosity — research, competitive academic wins, independent "
                                    "projects, faculty endorsement. "
                                    "Score 1: national academic competitions + faculty-mentored research + publications. "
                                    "Score 2: national competitions OR formal research with endorsement. "
                                    "Score 3: self-driven intellectual projects beyond coursework, no formal recognition. "
                                    "Score 4: limited evidence of scholarly curiosity. Score 5: none."
                                ),
                                "properties": {
                                    "score": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["score", "rationale"],
                            },
                            "athletic": {
                                "type": "object",
                                "description": (
                                    "Sports participation, varsity, competitions, physical discipline. "
                                    "Score 1: national/elite level athlete. Score 2: varsity + competition wins. "
                                    "Score 3: varsity or JV participation. Score 4: club/recreational only. "
                                    "Score 5: no athletic participation documented."
                                ),
                                "properties": {
                                    "score": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["score", "rationale"],
                            },
                            "personality": {
                                "type": "object",
                                "description": (
                                    "Resilience, empathy, leadership, authenticity, community contribution. "
                                    "Primarily assessed through personal essay — score null if no essay provided. "
                                    "Conversation signals (resilience, curiosity, values) can give a preliminary read. "
                                    "Score 1: exceptional story with clear values and impact. "
                                    "Score 2: compelling narrative with strong character signals. "
                                    "Score 3: decent character signals but limited story depth. "
                                    "Score 4: generic or unclear personality. Score 5: no signal."
                                ),
                                "properties": {
                                    "score": {"type": ["integer", "null"], "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["score", "rationale"],
                            },
                            "overall": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": (
                                    "Holistic composite weighted toward strengths. Not an average. "
                                    "Anchored by strongest core criteria. Score 1 = Harvard-level. "
                                    "Score 2 = top-15 highly likely. Score 3 = top-50 possible. "
                                    "Score 4 = selective schools difficult. Score 5 = well below competitive range."
                                ),
                            },
                            "priority_actions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "2-4 concrete, specific actions to improve college admissions chances.",
                            },
                        },
                        "required": [
                            "academic", "extracurriculars", "mind", "athletic",
                            "personality", "overall", "priority_actions",
                        ],
                    },
                    "entrepreneurship": {
                        "type": "object",
                        "description": (
                            "Venture Talent is the differentiating criterion. Prospective user interest does NOT count. "
                            "Paying customers, MRR, and engagement metrics are the only signals that move the needle."
                        ),
                        "properties": {
                            "skills_and_talent": {
                                "type": "object",
                                "description": (
                                    "Full-stack technical ability, domain knowledge, competition wins, credentials. "
                                    "Tier 1: competition wins + proven traction + internship experience. "
                                    "Tier 2: strong technical skills + some external validation. "
                                    "Tier 3-4: capable builder but no wins, traction, or validation. "
                                    "Tier 5: limited relevant skills."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "venture_talent": {
                                "type": "object",
                                "description": (
                                    "Actual traction ONLY — paying customers, MRR, active users, engagement metrics. "
                                    "Prospective interest or intent-to-subscribe does NOT count. "
                                    "Tier 1: significant MRR, thousands of active users. "
                                    "Tier 2: paying customers, measurable engagement. "
                                    "Tier 3: functional MVP, some non-paying users or interest. "
                                    "Tier 4: MVP without users. Tier 5: idea stage only."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "commitment_and_work_ethic": {
                                "type": "object",
                                "description": (
                                    "Time invested weekly, months of sustained effort, iteration beyond MVP, trade-offs made. "
                                    "Tier 1: full-time commitment, documented iteration history, explicit trade-offs. "
                                    "Tier 2: consistent part-time, multiple versions shipped. "
                                    "Tier 3: technically advanced MVP, no explicit time stated, no iteration history. "
                                    "Tier 4: brief or intermittent effort. Tier 5: minimal time invested."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "overall_tier": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": "Holistic entrepreneurship tier, anchored heavily by venture_talent.",
                            },
                            "priority_actions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "2-4 concrete, specific actions to move up to the next tier.",
                            },
                        },
                        "required": [
                            "skills_and_talent", "venture_talent", "commitment_and_work_ethic",
                            "overall_tier", "priority_actions",
                        ],
                    },
                    "research": {
                        "type": "object",
                        "description": (
                            "The ceiling without formal lab work or publications is Tier 3 regardless of "
                            "subject matter depth. Specificity is everything — named researchers, actual papers, "
                            "and exact methodologies separate Tier 2 from Tier 3."
                        ),
                        "properties": {
                            "scientific_depth_and_understanding": {
                                "type": "object",
                                "description": (
                                    "Specificity of knowledge — named labs, researchers, publications, mechanisms cited correctly. "
                                    "Tier 1: can name specific labs, researchers, cite papers, and describe exact methodologies. "
                                    "Tier 2: cites specific mechanisms and relevant publications accurately. "
                                    "Tier 3: can discuss specific mechanisms but names no specific labs/researchers. "
                                    "Tier 4: general subject knowledge, no specific citations. Tier 5: surface-level only."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "prior_experience_and_projects": {
                                "type": "object",
                                "description": (
                                    "Formal lab work, publications, poster presentations, advanced coursework. "
                                    "Tier 1: first-author publication or formal lab affiliation with output. "
                                    "Tier 2: formal lab work or poster presentation. "
                                    "Tier 3: strong academic foundation and research question, no formal lab. "
                                    "Tier 4: general interest but no structured work. Tier 5: no prior experience."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "commitment_and_learning": {
                                "type": "object",
                                "description": (
                                    "Months of dedicated study, consistency of engagement, deepening involvement. "
                                    "Tier 1: joined a lab, attending conferences, building community connections. "
                                    "Tier 2: months of dedicated self-directed learning, clear research question, systematic approach. "
                                    "Tier 3: several months of focused self-directed learning. "
                                    "Tier 4: recent or sporadic interest. Tier 5: no sustained commitment."
                                ),
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "rationale": {"type": "string"},
                                },
                                "required": ["rating", "rationale"],
                            },
                            "overall_tier": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "description": (
                                    "Holistic research tier. Hard cap at Tier 3 without formal lab work or publications."
                                ),
                            },
                            "priority_actions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "2-4 concrete, specific actions to move up to the next research tier.",
                            },
                        },
                        "required": [
                            "scientific_depth_and_understanding", "prior_experience_and_projects",
                            "commitment_and_learning", "overall_tier", "priority_actions",
                        ],
                    },
                },
                "required": ["internship_match", "college_chance", "entrepreneurship", "research"],
            },
        },
        "required": ["academic", "skills", "interests", "goals", "experience", "opportunity_ratings"],
    },
}

SYSTEM_PROMPT = """\
You are an expert college counselor and student profiler for Ultra, a platform that matches \
high school students to college programs, internships, research opportunities, and \
entrepreneurship resources.

You will receive a student's parsed resume data, the full transcript of their onboarding \
interview, and their GitHub activity data. Your job is to synthesize ALL of this into a \
structured, accurate, and honest student profile with rubric-based opportunity ratings.

Guidelines for the profile fields:
- Draw on the resume data, interview transcript, AND GitHub activity equally.
- Be specific — vague entries like "hardworking" are less useful than concrete evidence.

Guidelines for GitHub activity:
- Use the monthly_breakdown to assess contribution consistency and gaps.
- Use repo stars/forks as a proxy for community engagement and external validation.
- Use top_languages and repo descriptions to corroborate technical skill claims.
- A month with fewer than 5 contributions counts as a notable dip.

Guidelines for opportunity_ratings:
- Ratings use a 1–5 scale where 1 = Tier 1 (strongest) and 5 = Tier 5 (weakest/unranked).
- Be honest — these ratings guide students' development. Flattery is harmful.
- Each criterion has a detailed description in the tool schema — follow it precisely.

Key rubric anchors to enforce strictly:
- INTERNSHIP: Tier is determined by external validation and demonstrated output (shipped \
  products, GitHub stars, competition wins). Self-reported skill depth alone cannot reach Tier 1. \
  Use GitHub data directly when rating Work Ethic & Output and Development Experience.
- COLLEGE CHANCE: Overall score is NOT an average. It weights strengths and ignores weak areas \
  like athletics if they are absent. A Score 1 is Harvard-caliber across all core criteria.
- ENTREPRENEURSHIP: Venture Talent is the differentiating criterion. Prospective user interest \
  and intent-to-subscribe do NOT count. Only paying customers, MRR, and active engagement metrics \
  move the needle. An MVP without paying users is Tier 3 at best.
- RESEARCH: The ceiling without formal lab work or publications is Tier 3, regardless of subject \
  matter depth. Named researchers, actual papers, and exact methodologies separate Tier 2 from Tier 3.

Use the create_student_profile tool to return your output.
"""


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
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[PROFILE_TOOL],
        tool_choice={"type": "tool", "name": "create_student_profile"},
        messages=[{"role": "user", "content": user_message}],
    )

    for block in response.content:
        if hasattr(block, "type") and block.type == "tool_use" and block.name == "create_student_profile":
            return block.input

    raise RuntimeError("Synthesizer did not return a student profile")
