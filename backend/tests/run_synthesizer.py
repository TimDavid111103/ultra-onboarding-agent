"""
Usage:
  python tests/run_synthesizer.py                          # runs default profile
  python tests/run_synthesizer.py profiles/my_profile.json
  python tests/run_synthesizer.py profiles/my_profile.json --full
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from agents.synthesizer import synthesize_profile

DEFAULT_FIXTURE = Path(__file__).parent / "profiles"

VERTICAL_KEYS = {
    "Internship Match":  "internship_match",
    "College Chance":    "college_chance",
    "Entrepreneurship":  "entrepreneurship",
    "Research":          "research",
}

SUBCATEGORY_LABELS = {
    "internship_match": [
        ("Skills & Talent",        "skills_and_talent"),
        ("Development Experience", "development_experience"),
        ("Work Ethic & Output",    "work_ethic_and_output"),
    ],
    "college_chance": [
        ("Academic",        "academic"),
        ("Extracurriculars","extracurriculars"),
        ("Mind",            "mind"),
        ("Athletic",        "athletic"),
        ("Personality",     "personality"),
    ],
    "entrepreneurship": [
        ("Skills & Talent",       "skills_and_talent"),
        ("Venture Talent",        "venture_talent"),
        ("Commitment & Work Ethic","commitment_and_work_ethic"),
    ],
    "research": [
        ("Scientific Depth",      "scientific_depth_and_understanding"),
        ("Prior Experience",      "prior_experience_and_projects"),
        ("Commitment & Learning", "commitment_and_learning"),
    ],
}


def confidence_label(score: int) -> str:
    if score >= 80:
        return f"● {score}%  [HIGH]"
    if score >= 50:
        return f"● {score}%  [MED]"
    return f"● {score}%  [LOW]"


def load_fixture(path: Path) -> tuple[dict, list[dict], dict | None]:
    data = json.loads(path.read_text())
    return data["resume_data"], data["conversation"], data.get("github_activity")


def print_profile(profile: dict, full: bool = False) -> None:
    opp = profile.get("opportunity_ratings", {})

    # ── Signal confidence overview ────────────────────────
    print("\n── Signal Confidence ────────────────────────────────")
    for label, key in VERTICAL_KEYS.items():
        block = opp.get(key, {})
        score = block.get("confidence", "?")
        cl = confidence_label(score) if isinstance(score, int) else str(score)
        print(f"  {label:<22} {cl}")

    # ── Per-vertical detail ───────────────────────────────
    for label, key in VERTICAL_KEYS.items():
        block = opp.get(key, {})
        print(f"\n{'━' * 52}")
        print(f"  {label}  —  {confidence_label(block.get('confidence', '?'))}")
        print(f"{'━' * 52}")

        summary = block.get("summary", "")
        if summary:
            print(f"\n  {summary}")

        for sub_label, sub_key in SUBCATEGORY_LABELS.get(key, []):
            sub = block.get(sub_key, {})
            ctx = sub.get("context", "")
            sub_score = sub.get("confidence", "?")
            sub_cl = confidence_label(sub_score) if isinstance(sub_score, int) else str(sub_score)
            if ctx:
                print(f"\n  [{sub_label}]  {sub_cl}")
                # Word-wrap at ~72 chars
                words, line = ctx.split(), ""
                for word in words:
                    if len(line) + len(word) + 1 > 72:
                        print(f"    {line}")
                        line = word
                    else:
                        line = f"{line} {word}".strip()
                if line:
                    print(f"    {line}")

        key_points = block.get("key_points", [])
        if key_points:
            print(f"\n  Key Points")
            for pt in key_points:
                print(f"    → {pt}")

    # ── Skills / Interests / Goals ────────────────────────
    print(f"\n{'━' * 52}")
    print("  Skills / Interests / Goals")
    print(f"{'━' * 52}")

    skills = profile.get("skills", {})
    tech = skills.get("technical", [])
    soft = skills.get("soft", [])
    if tech:
        print(f"\n  Technical:  {', '.join(tech)}")
    if soft:
        print(f"  Soft:       {', '.join(soft)}")

    interests = profile.get("interests", [])
    if interests:
        print(f"  Interests:  {', '.join(interests)}")

    goals = profile.get("goals", {})
    if goals.get("career_direction"):
        print(f"  Career:     {goals['career_direction']}")
    if goals.get("college_targets"):
        print(f"  Colleges:   {', '.join(goals['college_targets'])}")
    if goals.get("research_interests"):
        print(f"  Research:   {', '.join(goals['research_interests'])}")

    if full:
        print(f"\n{'━' * 52}")
        print("  Full Profile JSON")
        print(f"{'━' * 52}")
        print(json.dumps(profile, indent=2))


def main() -> None:
    args = sys.argv[1:]
    full = "--full" in args
    args = [a for a in args if not a.startswith("--")]

    if args:
        profile_path = Path(args[0])
        if not profile_path.is_absolute():
            profile_path = Path.cwd() / profile_path
    else:
        profiles = sorted(DEFAULT_FIXTURE.glob("*.json"))
        if not profiles:
            print("No profiles found.", file=sys.stderr)
            sys.exit(1)
        profile_path = profiles[0]

    if not profile_path.exists():
        print(f"Profile not found: {profile_path}", file=sys.stderr)
        sys.exit(1)

    description = json.loads(profile_path.read_text()).get("_description", "")
    if description:
        print(f"\nProfile: {profile_path.name}")
        print(f"Notes:   {description}")

    print("\nRunning synthesizer… (this makes a live API call)")
    resume_data, conversation, github_activity = load_fixture(profile_path)
    if github_activity:
        print(f"GitHub activity: {github_activity['total_contributions_last_6_months']} contributions over 6 months")

    profile = synthesize_profile(resume_data, conversation, github_activity)
    print_profile(profile, full=full)


if __name__ == "__main__":
    main()
