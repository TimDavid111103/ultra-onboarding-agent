"""
Generate a resume PDF from a test profile JSON's resume_data.
Use the output to upload into the browser app as a real student resume.

Usage (from backend/):
  python tests/export_pdf.py tests/profiles/maya_chen.json
  python tests/export_pdf.py tests/profiles/jason_park.json

Output: <profile_stem>_resume.pdf saved in the current directory.
"""
import json
import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

W, _ = letter
MARGIN = 0.75 * inch

BLACK = colors.HexColor("#111111")
GRAY  = colors.HexColor("#555555")
SILVER = colors.HexColor("#cccccc")


def S(name, **kw):
    base = dict(fontName="Helvetica", fontSize=10, leading=14, textColor=BLACK)
    base.update(kw)
    return ParagraphStyle(name, **base)


STYLES = {
    "name":    S("name",    fontName="Helvetica-Bold", fontSize=20, leading=24),
    "section": S("section", fontName="Helvetica-Bold", fontSize=10, spaceBefore=8, spaceAfter=2),
    "body":    S("body",    fontSize=9.5, leading=13),
    "sub":     S("sub",     fontSize=9.5, leading=13, textColor=GRAY),
    "bullet":  S("bullet",  fontSize=9.5, leading=13, leftIndent=12),
}


def section(title, story):
    story.append(Paragraph(title.upper(), STYLES["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SILVER, spaceAfter=4))


def build_resume(profile_path: Path) -> Path:
    data = json.loads(profile_path.read_text())
    r = data["resume_data"]
    out = Path.home() / "Desktop" / f"{profile_path.stem}_resume.pdf"

    doc = SimpleDocTemplate(str(out), pagesize=letter,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN)
    story = []

    # Name
    story.append(Paragraph(r.get("name", "Student"), STYLES["name"]))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLACK, spaceAfter=6))

    # Education
    section("Education", story)
    grad = r.get("graduation_year")
    gpa = r.get("gpa")
    scores = r.get("test_scores", {})
    sat = scores.get("SAT")
    act = scores.get("ACT")

    edu_parts = []
    if grad:
        edu_parts.append(f"Expected graduation: {grad}")
    if gpa:
        edu_parts.append(f"GPA: {gpa:.2f} unweighted")
    if sat:
        edu_parts.append(f"SAT: {sat}")
    if act:
        edu_parts.append(f"ACT: {act}")
    story.append(Paragraph(" · ".join(edu_parts), STYLES["body"]))

    courses = r.get("courses", [])
    if courses:
        story.append(Spacer(1, 3))
        story.append(Paragraph("<b>Coursework:</b> " + ", ".join(courses), STYLES["body"]))

    # Activities
    activities = r.get("activities", [])
    if activities:
        section("Extracurriculars", story)
        for a in activities:
            story.append(Paragraph(f"• {a}", STYLES["bullet"]))

    # Work Experience
    work = r.get("work_experience", [])
    if work:
        section("Work Experience", story)
        for w in work:
            story.append(Paragraph(f"• {w}", STYLES["bullet"]))

    # Skills
    skills = r.get("skills", [])
    if skills:
        section("Skills", story)
        story.append(Paragraph(", ".join(skills), STYLES["body"]))

    # Awards
    awards = r.get("awards", [])
    if awards:
        section("Awards & Recognition", story)
        for a in awards:
            story.append(Paragraph(f"• {a}", STYLES["bullet"]))

    # Summary / About
    summary = r.get("summary_detected", "").strip()
    if summary:
        section("About", story)
        story.append(Paragraph(f'"{summary}"', STYLES["sub"]))

    doc.build(story)
    return out


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python tests/export_pdf.py tests/profiles/<name>.json", file=sys.stderr)
        sys.exit(1)

    profile_path = Path(args[0])
    if not profile_path.is_absolute():
        profile_path = Path.cwd() / profile_path
    if not profile_path.exists():
        print(f"Profile not found: {profile_path}", file=sys.stderr)
        sys.exit(1)

    out = build_resume(profile_path)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
