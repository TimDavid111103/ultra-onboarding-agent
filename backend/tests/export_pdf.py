"""
Generate a student profile PDF from a test profile JSON.

Usage (from backend/):
  python tests/export_pdf.py tests/profiles/maya_chen.json
  python tests/export_pdf.py tests/profiles/jason_park.json

Output: <profile_stem>_report.pdf saved in the current directory.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from agents.synthesizer import synthesize_profile
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether,
)

W, _ = letter
MARGIN = 0.75 * inch
USABLE = W - 2 * MARGIN

BLACK   = colors.HexColor("#111111")
GRAY    = colors.HexColor("#555555")
SILVER  = colors.HexColor("#cccccc")
PURPLE  = colors.HexColor("#6b5a9e")
OFFWHITE = colors.HexColor("#fafafa")


def S(name, **kw):
    defaults = dict(fontName="Helvetica", fontSize=9, leading=13, textColor=BLACK)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)


STYLES = {
    "name":     S("name",    fontName="Helvetica-Bold", fontSize=22, leading=26),
    "sub":      S("sub",     fontSize=10, textColor=GRAY),
    "section":  S("section", fontName="Helvetica-Bold", fontSize=9, textColor=GRAY, spaceBefore=10),
    "body":     S("body",    fontSize=8.5, leading=12),
    "small":    S("small",   fontSize=8, leading=11, textColor=GRAY),
    "area":     S("area",    fontName="Helvetica-Bold", fontSize=11, leading=14),
    "tier":     S("tier",    fontName="Helvetica-Bold", fontSize=14, textColor=PURPLE, alignment=2),
    "tierlabel":S("tierlabel", fontSize=8, textColor=PURPLE),
    "bullet":   S("bullet",  fontSize=8.5, leading=12, leftIndent=10),
    "cell":     S("cell",    fontName="Helvetica-Bold", fontSize=9, textColor=PURPLE, alignment=1),
}

TIER_LABELS = {1: "Exceptional", 2: "Strong", 3: "Developing", 4: "Early Stage", 5: "Not Yet Ready"}

AREAS = [
    ("Internship Match",  "internship_match",  "overall_tier", [
        ("Skills & Talent",        "skills_and_talent",      "rating"),
        ("Development Experience", "development_experience",  "rating"),
        ("Work Ethic & Output",    "work_ethic_and_output",  "rating"),
    ]),
    ("College Chance",   "college_chance",    "overall",      [
        ("Academic",               "academic",        "score"),
        ("Extracurriculars",       "extracurriculars","score"),
        ("Mind",                   "mind",            "score"),
        ("Athletic",               "athletic",        "score"),
        ("Personality",            "personality",     "score"),
    ]),
    ("Entrepreneurship", "entrepreneurship",  "overall_tier", [
        ("Skills & Talent",  "skills_and_talent",         "rating"),
        ("Venture Talent",   "venture_talent",            "rating"),
        ("Commitment",       "commitment_and_work_ethic", "rating"),
    ]),
    ("Research",         "research",          "overall_tier", [
        ("Scientific Depth",      "scientific_depth_and_understanding", "rating"),
        ("Prior Experience",      "prior_experience_and_projects",      "rating"),
        ("Commitment & Learning", "commitment_and_learning",            "rating"),
    ]),
]


def build_pdf(profile_path: Path, synthesized: dict) -> Path:
    out = Path.cwd() / f"{profile_path.stem}_report.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=letter,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN)
    raw = json.loads(profile_path.read_text())
    resume = raw.get("resume_data", {})

    academic = synthesized.get("academic", {})
    scores = academic.get("test_scores", {})
    sat = scores.get("SAT")
    act = scores.get("ACT")
    gpa = academic.get("gpa") or resume.get("gpa")
    grad = academic.get("graduation_year") or resume.get("graduation_year")

    score_str = " · ".join(filter(None, [f"SAT {sat}" if sat else None, f"ACT {act}" if act else None]))

    story = []

    # Header
    story.append(Paragraph(resume.get("name", "Student"), STYLES["name"]))
    parts = [p for p in [
        f"Class of {grad}" if grad else None,
        f"GPA {gpa:.2f}" if gpa else None,
        score_str or None,
    ] if p]
    story.append(Paragraph(" · ".join(parts), STYLES["sub"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=SILVER))
    story.append(Spacer(1, 6))

    # Courses
    courses = academic.get("courses", [])
    if courses:
        story.append(Paragraph("COURSEWORK", STYLES["section"]))
        story.append(Paragraph(", ".join(courses), STYLES["body"]))

    # Skills
    skills = synthesized.get("skills", {})
    tech = skills.get("technical", [])
    if tech:
        story.append(Paragraph("SKILLS", STYLES["section"]))
        story.append(Paragraph(", ".join(tech), STYLES["body"]))

    # Goals
    goals = synthesized.get("goals", {})
    targets = goals.get("college_targets", [])
    career = goals.get("career_direction", "")
    research_ints = goals.get("research_interests", [])
    if targets or career:
        story.append(Paragraph("GOALS", STYLES["section"]))
        if targets:
            story.append(Paragraph(f"<b>Targets:</b> {', '.join(targets)}", STYLES["body"]))
        if career:
            story.append(Paragraph(f"<b>Direction:</b> {career}", STYLES["body"]))
        if research_ints:
            story.append(Paragraph(f"<b>Research interests:</b> {', '.join(research_ints)}", STYLES["body"]))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=SILVER))
    story.append(Spacer(1, 4))
    story.append(Paragraph("OPPORTUNITY RATINGS  ·  1 = Exceptional  →  5 = Not Yet Ready", STYLES["section"]))
    story.append(Spacer(1, 6))

    ratings = synthesized.get("opportunity_ratings", {})

    for area_label, area_key, overall_key, subcriteria in AREAS:
        block = ratings.get(area_key, {})
        overall = block.get(overall_key, "?")
        tier_text = TIER_LABELS.get(overall, "") if isinstance(overall, int) else ""

        elems = []

        header = Table([[
            Paragraph(area_label.upper(), STYLES["area"]),
            Paragraph(f"<b>{overall}</b> / 5", STYLES["tier"]),
        ]], colWidths=[USABLE * 0.75, USABLE * 0.25])
        header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        elems.append(header)
        if tier_text:
            elems.append(Paragraph(tier_text, STYLES["tierlabel"]))
        elems.append(Spacer(1, 4))

        rows = [["Criterion", "Rating", "Rationale"]]
        for sub_label, sub_key, val_key in subcriteria:
            sub = block.get(sub_key, {})
            if not isinstance(sub, dict):
                continue
            val = sub.get(val_key)
            rationale = sub.get("rationale", "")
            if val is None:
                continue
            rows.append([
                Paragraph(sub_label, STYLES["body"]),
                Paragraph(f"<b>{val}</b>", STYLES["cell"]),
                Paragraph(rationale[:130] + ("…" if len(rationale) > 130 else ""), STYLES["small"]),
            ])

        tbl = Table(rows, colWidths=[USABLE * 0.22, USABLE * 0.08, USABLE * 0.70])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 7.5),
            ("TEXTCOLOR",     (0, 0), (-1, 0), GRAY),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, OFFWHITE]),
            ("GRID",          (0, 0), (-1, -1), 0.25, SILVER),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elems.append(tbl)

        actions = block.get("priority_actions", [])
        if actions:
            elems.append(Spacer(1, 3))
            elems.append(Paragraph("<b>Priority actions</b>", STYLES["small"]))
            for a in actions:
                elems.append(Paragraph(f"→ {a}", STYLES["bullet"]))

        elems.append(Spacer(1, 10))
        story.append(KeepTogether(elems))

    doc.build(story)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Usage: python tests/export_pdf.py tests/profiles/<name>.json", file=sys.stderr)
        sys.exit(1)

    profile_path = Path(args[0])
    if not profile_path.is_absolute():
        profile_path = Path.cwd() / profile_path
    if not profile_path.exists():
        print(f"Profile not found: {profile_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(profile_path.read_text())
    print(f"Synthesizing profile for {data['resume_data'].get('name', 'student')}… (live API call)")
    profile = synthesize_profile(data["resume_data"], data["conversation"], data.get("github_activity"))

    print("Generating PDF…")
    out = build_pdf(profile_path, profile)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
