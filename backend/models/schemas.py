from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# ---------- Session store ----------

@dataclass
class Session:
    session_id: str
    resume_data: dict[str, Any]
    conversation: list[dict[str, str]] = field(default_factory=list)
    profile: dict[str, Any] | None = None
    is_complete: bool = False
    coverage: dict[str, int] = field(default_factory=lambda: {
        "academics": 0,
        "extracurriculars": 0,
        "experience_and_projects": 0,
        "goals_and_interests": 0,
        "character_and_drive": 0,
    })


# ---------- GitHub activity input ----------
# Passed into synthesize_profile() alongside resume_data and conversation.
# Live app uses DEFAULT_GITHUB_ACTIVITY from agents/github_activity.py.
# Tests supply their own block via fixture files.
#
# GitHubActivity shape:
# {
#   "total_contributions_last_6_months": int,
#   "monthly_breakdown": {"YYYY-MM": int, ...}, 
#   "public_repos": int,
#   "top_repos": [{"name": str, "stars": int, "forks": int,
#                  "primary_language": str, "description": str}],
#   "top_languages": list[str],
#   "longest_streak_days": int,
#   "account_age_years": int,
# }


# ---------- Resume parser output ----------
# Returned as a plain dict by the agent; typed here for reference.
#
# ResumeData shape:
# {
#   "name": str,
#   "graduation_year": int | None,
#   "gpa": float | None,
#   "test_scores": {"SAT": int | None, "ACT": int | None},
#   "courses": list[str],
#   "activities": list[str],
#   "work_experience": list[str],
#   "skills": list[str],
#   "awards": list[str],
#   "summary_detected": str,
# }


# ---------- Student profile output ----------
# Returned as a plain dict by the synthesizer; typed here for reference.
#
# StudentProfile shape:
# {
#   "academic": {
#     "gpa": float | None,
#     "test_scores": {"SAT": int | None, "ACT": int | None},
#     "courses": list[str],
#     "graduation_year": int | None,
#   },
#   "skills": {"technical": list[str], "soft": list[str]},
#   "interests": list[str],
#   "goals": {
#     "college_targets": list[str],
#     "career_direction": str,
#     "research_interests": list[str],
#   },
#   "experience": [{"title": str, "org": str, "description": str}],
#   "opportunity_ratings": {
#     "internship_match": {
#       "skills_and_talent": {"rating": int 1-5, "rationale": str},
#       "development_experience": {"rating": int 1-5, "rationale": str},
#       "work_ethic_and_output": {"rating": int 1-5, "rationale": str},
#       "overall_tier": int 1-5,
#       "priority_actions": list[str],
#     },
#     "college_chance": {
#       "academic": {"score": int 1-5, "rationale": str},
#       "extracurriculars": {"score": int 1-5, "rationale": str},
#       "mind": {"score": int 1-5, "rationale": str},
#       "athletic": {"score": int 1-5, "rationale": str},
#       "personality": {"score": int | None 1-5, "rationale": str},
#       "overall": int 1-5,
#       "priority_actions": list[str],
#     },
#     "entrepreneurship": {
#       "skills_and_talent": {"rating": int 1-5, "rationale": str},
#       "venture_talent": {"rating": int 1-5, "rationale": str},
#       "commitment_and_work_ethic": {"rating": int 1-5, "rationale": str},
#       "overall_tier": int 1-5,
#       "priority_actions": list[str],
#     },
#     "research": {
#       "scientific_depth_and_understanding": {"rating": int 1-5, "rationale": str},
#       "prior_experience_and_projects": {"rating": int 1-5, "rationale": str},
#       "commitment_and_learning": {"rating": int 1-5, "rationale": str},
#       "overall_tier": int 1-5,
#       "priority_actions": list[str],
#     },
#   },
# }
