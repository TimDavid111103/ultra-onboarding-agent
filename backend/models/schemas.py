from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


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


# ---------- Student profile output ----------

class SubcategoryContext(BaseModel):
    confidence: int = Field(
        ge=0, le=100,
        description=(
            "0–100 confidence that the downstream agent will find scoreable signal for this subcategory "
            "based on its grading rubric. This is NOT a rating of the student and NOT a measure of how "
            "much the conversation talked about this topic. Score based strictly on how well the known "
            "information about the student maps to what this subcategory's rubric actually evaluates. "
            "80–100: strong rubric-relevant evidence present. 50–79: partial evidence, gaps remain. "
            "0–49: little or no rubric-relevant evidence."
        )
    )
    context: str = Field(
        description=(
            "2–4 sentences drawn entirely from what the student said in the interview. "
            "Do not restate resume facts — surface what the conversation revealed beyond the resume."
        )
    )


class InternshipMatchSection(BaseModel):
    confidence: int = Field(
        ge=0, le=100,
        description=(
            "0–100 confidence that the Internship Match agent will find scoreable signal across its rubric "
            "(Skills & Talent, Development Experience, Work Ethic & Output). Score based on how well the "
            "student's known information maps to that rubric — not on how much the topic came up. "
            "NOT a rating of the student."
        )
    )
    summary: str = Field(description="Exactly two sentences summarizing the internship signal from the conversation.")
    skills_and_talent: SubcategoryContext = Field(
        description="Technical depth, tools used, competitive wins, and validation signals the student described."
    )
    development_experience: SubcategoryContext = Field(
        description="Project scope, complexity, real-world output, and ownership the student described."
    )
    work_ethic_and_output: SubcategoryContext = Field(
        description="Consistency, output pace, and effort patterns the student described."
    )
    key_points: list[str] = Field(
        description=(
            "3–4 bullets of the most notable things the conversation revealed about this student "
            "that the resume alone would not show."
        )
    )


class CollegeChanceSection(BaseModel):
    confidence: int = Field(
        ge=0, le=100,
        description=(
            "0–100 confidence that the College Chance agent will find scoreable signal across its rubric "
            "(Academic, Extracurriculars, Mind, Athletic, Personality). Score based on how well the "
            "student's known information maps to that rubric — not on how much the topic came up. "
            "NOT a rating of the student."
        )
    )
    summary: str = Field(description="Exactly two sentences summarizing the college admissions signal from the conversation.")
    academic: SubcategoryContext = Field(
        description="Intellectual engagement, curiosity, and academic context beyond GPA/scores the student revealed."
    )
    extracurriculars: SubcategoryContext = Field(
        description="Depth, leadership, impact, and personal meaning of activities the student described."
    )
    mind: SubcategoryContext = Field(
        description="Scholarly drive, research engagement, independent intellectual work the student described."
    )
    athletic: SubcategoryContext = Field(
        description="Athletic involvement or physical pursuits the student mentioned. Note if none came up."
    )
    personality: SubcategoryContext = Field(
        description="Character, resilience, self-awareness, values, and personal narrative that emerged in conversation."
    )
    key_points: list[str] = Field(
        description=(
            "3–4 bullets of the most notable things the conversation revealed about this student "
            "that the resume alone would not show."
        )
    )


class EntrepreneurshipSection(BaseModel):
    confidence: int = Field(
        ge=0, le=100,
        description=(
            "0–100 confidence that the Entrepreneurship agent will find scoreable signal across its rubric "
            "(Skills & Talent, Venture Talent, Commitment & Work Ethic). Score based on how well the "
            "student's known information maps to that rubric — not on how much the topic came up. "
            "NOT a rating of the student."
        )
    )
    summary: str = Field(description="Exactly two sentences summarizing the entrepreneurship signal from the conversation.")
    skills_and_talent: SubcategoryContext = Field(
        description="Technical and domain skills relevant to building products that the student revealed."
    )
    venture_talent: SubcategoryContext = Field(
        description="Any traction, customers, products, or entrepreneurial thinking the student described. Note if explicitly absent."
    )
    commitment_and_work_ethic: SubcategoryContext = Field(
        description="Sustained effort, iteration, and trade-offs the student described — even outside entrepreneurial contexts."
    )
    key_points: list[str] = Field(
        description=(
            "3–4 bullets of the most notable things the conversation revealed about this student "
            "that the resume alone would not show."
        )
    )


class ResearchSection(BaseModel):
    confidence: int = Field(
        ge=0, le=100,
        description=(
            "0–100 confidence that the Research agent will find scoreable signal across its rubric "
            "(Scientific Depth & Understanding, Prior Experience & Projects, Commitment & Learning). "
            "Score based on how well the student's known information maps to that rubric — not on how "
            "much the topic came up. NOT a rating of the student."
        )
    )
    summary: str = Field(description="Exactly two sentences summarizing the research signal from the conversation.")
    scientific_depth_and_understanding: SubcategoryContext = Field(
        description="Specific knowledge, named researchers, mechanisms, papers, and lab details the student described."
    )
    prior_experience_and_projects: SubcategoryContext = Field(
        description="Formal lab work, publications, posters, and structured research the student described."
    )
    commitment_and_learning: SubcategoryContext = Field(
        description="Sustained engagement, intellectual growth, and deepening involvement the student described."
    )
    key_points: list[str] = Field(
        description=(
            "3–4 bullets of the most notable things the conversation revealed about this student "
            "that the resume alone would not show."
        )
    )


class OpportunityRatings(BaseModel):
    internship_match: InternshipMatchSection
    college_chance: CollegeChanceSection
    entrepreneurship: EntrepreneurshipSection
    research: ResearchSection


class Skills(BaseModel):
    technical: list[str] = Field(description="Technical skills surfaced from both resume and conversation.")
    soft: list[str] = Field(description="Soft skills and character traits surfaced from the conversation, not the resume.")


class Goals(BaseModel):
    college_targets: list[str] = Field(description="Schools mentioned in the conversation.")
    career_direction: str = Field(description="Career direction as the student articulated it in the conversation.")
    research_interests: list[str] = Field(description="Specific research topics the student described in the conversation.")


class StudentProfile(BaseModel):
    skills: Skills
    interests: list[str] = Field(
        description="Topics, domains, and pursuits the student expressed genuine interest in during the conversation."
    )
    goals: Goals
    opportunity_ratings: OpportunityRatings
