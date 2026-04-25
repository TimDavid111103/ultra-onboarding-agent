# Default GitHub activity injected when running the live app.
# Tests supply their own github_activity block via fixture files.
#
# GitHubActivity shape:
# {
#   "total_contributions_last_6_months": int,
#   "monthly_breakdown": {          # keys are calendar month strings, values are int counts
#       "YYYY-MM": int,
#       ...
#   },
#   "public_repos": int,
#   "top_repos": [
#       {
#           "name": str,
#           "stars": int,
#           "forks": int,
#           "primary_language": str,
#           "description": str,
#       },
#       ...
#   ],
#   "top_languages": list[str],
#   "longest_streak_days": int,
#   "account_age_years": int,
# }

DEFAULT_GITHUB_ACTIVITY: dict = {
    "total_contributions_last_6_months": 58,
    "monthly_breakdown": {
        "month_6_ago": 14,
        "month_5_ago": 9,
        "month_4_ago": 4,
        "month_3_ago": 16,
        "month_2_ago": 7,
        "month_1_ago": 8,
    },
    "public_repos": 4,
    "top_repos": [
        {
            "name": "school-assignments",
            "stars": 0,
            "forks": 0,
            "primary_language": "Python",
            "description": "",
        },
        {
            "name": "personal-site",
            "stars": 0,
            "forks": 0,
            "primary_language": "HTML",
            "description": "",
        },
    ],
    "top_languages": ["Python", "HTML"],
    "longest_streak_days": 6,
    "account_age_years": 1,
}
