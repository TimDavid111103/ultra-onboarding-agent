"""
Usage:
  python tests/run_synthesizer.py                          # runs default profile
  python tests/run_synthesizer.py profiles/my_profile.json
  python tests/run_synthesizer.py profiles/my_profile.json --ratings-only
"""
import json
import sys
from pathlib import Path

# Make backend/ importable when running from backend/ or project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from agents.synthesizer import synthesize_profile

DEFAULT_FIXTURE = Path(__file__).parent / "profiles"


def load_fixture(path: Path) -> tuple[dict, list[dict], dict | None]:
    data = json.loads(path.read_text())
    return data["resume_data"], data["conversation"], data.get("github_activity")


def print_ratings_summary(profile: dict) -> None:
    ratings = profile.get("opportunity_ratings", {})
    areas = {
        "Internship Match":    ("overall_tier",  ratings.get("internship_match",  {})),
        "College Chance":      ("overall",        ratings.get("college_chance",    {})),
        "Entrepreneurship":    ("overall_tier",   ratings.get("entrepreneurship",  {})),
        "Research":            ("overall_tier",   ratings.get("research",          {})),
    }
    print("\n── Opportunity Ratings Summary ──────────────────────")
    for area, (key, block) in areas.items():
        overall = block.get(key, "?")
        label = "Score" if area == "College Chance" else "Tier"
        print(f"  {area:<22} {label} {overall}")

    print("\n── Subcriteria ──────────────────────────────────────")
    subcriteria_map = {
        "Internship Match": [
            ("Skills & Talent",       "skills_and_talent",       "rating"),
            ("Development Experience","development_experience",   "rating"),
            ("Work Ethic & Output",   "work_ethic_and_output",   "rating"),
        ],
        "College Chance": [
            ("Academic",              "academic",       "score"),
            ("Extracurriculars",      "extracurriculars","score"),
            ("Mind",                  "mind",           "score"),
            ("Athletic",              "athletic",       "score"),
            ("Personality",           "personality",    "score"),
            ("Overall (holistic)",    "overall",        None),
        ],
        "Entrepreneurship": [
            ("Skills & Talent",       "skills_and_talent",          "rating"),
            ("Venture Talent",        "venture_talent",             "rating"),
            ("Commitment",            "commitment_and_work_ethic",  "rating"),
        ],
        "Research": [
            ("Scientific Depth",      "scientific_depth_and_understanding","rating"),
            ("Prior Experience",      "prior_experience_and_projects",    "rating"),
            ("Commitment & Learning", "commitment_and_learning",          "rating"),
        ],
    }
    area_key_map = {
        "Internship Match": "internship_match",
        "College Chance":   "college_chance",
        "Entrepreneurship": "entrepreneurship",
        "Research":         "research",
    }
    for area, criteria in subcriteria_map.items():
        block = ratings.get(area_key_map[area], {})
        print(f"\n  {area}")
        for display_name, field, value_key in criteria:
            if value_key is None:
                # flat integer field (e.g. college_chance.overall — not an average,
                # weighted toward strengths; anchored by strongest core criteria)
                val = block.get(field, "?")
                print(f"    {display_name:<24} {val}  — weighted toward strengths, not an average")
            else:
                sub = block.get(field, {})
                val = sub.get(value_key, "?")
                rationale = sub.get("rationale", "")
                print(f"    {display_name:<24} {val}  — {rationale[:80]}{'…' if len(rationale) > 80 else ''}")

    print("\n── Priority Actions ─────────────────────────────────")
    for area, area_key in area_key_map.items():
        actions = ratings.get(area_key, {}).get("priority_actions", [])
        if actions:
            print(f"\n  {area}")
            for action in actions:
                print(f"    → {action}")


def main() -> None:
    args = sys.argv[1:]
    ratings_only = "--ratings-only" in args
    args = [a for a in args if not a.startswith("--")]

    if args:
        profile_path = Path(args[0])
        if not profile_path.is_absolute():
            profile_path = Path(__file__).parent / profile_path
    else:
        profiles = sorted(DEFAULT_FIXTURE.glob("*.json"))
        if not profiles:
            print("No profiles found. Add a JSON file to tests/profiles/ or pass a path as an argument.", file=sys.stderr)
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

    if ratings_only:
        print_ratings_summary(profile)
    else:
        print_ratings_summary(profile)
        print("\n── Full Profile JSON ────────────────────────────────")
        print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
