DOWNSTREAM_RUBRICS = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOWNSTREAM AGENT GRADING RUBRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

These are the exact rubrics the four downstream agents use to evaluate students.
Use them to determine what conversation coverage is relevant and to set confidence
scores accurately.

──────────────────────────────────────────────────────────────
INTERNSHIP MATCH
"Tier is determined by external validation and demonstrated output as much as raw
technical ability. Shipping something real that others use or engage with is the
primary signal."
──────────────────────────────────────────────────────────────

Skills & Talent
  Measures: Technical stack depth, algorithmic aptitude, competition wins, external validation.
  Tier 1: National competition wins (USACO Platinum, Codeforces, top hackathons) + high-visibility open source.
  Tier 2: Strong technical stack + some external validation (stars, forks, hackathon placement).
  Tier 3: Advanced skills (e.g. async Python, AI pipelines, consistent GitHub) — but no competitive wins or community traction.
  Tier 4: Developing skills, limited portfolio. Tier 5: Minimal technical evidence.
  How to move up: Win a hackathon, compete in USACO/Codeforces, contribute to high-visibility open source.

Development Experience
  Measures: Project complexity, code quality, repo health (stars, forks, docs, tests).
  Tier 1: Production systems with real users, strong code quality, community engagement.
  Tier 2: Complex projects, some community engagement (stars/forks/contributors).
  Tier 3: Well-architected personal projects — but zero stars/forks, code quality ~6/10.
  Tier 4: Basic projects, limited complexity. Tier 5: Minimal project evidence.
  How to move up: Add tests, stronger typing, documentation; promote repos to gain engagement.

Work Ethic & Output
  Measures: GitHub contribution frequency, monthly distribution, sustained effort.
  Tier 1: Consistent daily activity, no dips, thorough documentation.
  Tier 2: Steady monthly contributions, minor dips.
  Tier 3: Active but notable dips (e.g. <5 contributions in a month).
  Tier 4: Inconsistent, many gaps. Tier 5: Minimal contribution history.
  How to move up: Maintain even monthly distribution; document work thoroughly.

──────────────────────────────────────────────────────────────
COLLEGE CHANCE
"Overall score is not an average — it weights strengths and ignores athletics if
not strong. All overall 1s got into Harvard. Over 50% of 2s got in."
──────────────────────────────────────────────────────────────

Academic
  Measures: GPA, test scores, class rank, coursework rigor.
  Score 1: Top 1% nationally, near-perfect GPA/scores, explicit class rank, most rigorous available coursework.
  Score 2: Strong GPA/scores with class rank provided.
  Score 3: Strong GPA/scores but missing rank or course detail (e.g. 3.99 UW, 1580 SAT — but no class rank).
  Score 4: Below-competitive stats. Score 5: Significantly below competitive range.
  How to move up: Provide explicit class rank (top 1–2%), list advanced coursework in full detail.

Extracurriculars
  Measures: Leadership roles, measurable impact, scale of recognition.
  Score 1: National recognition, major leadership, published or nationally awarded.
  Score 2: Regional recognition or significant school-wide leadership.
  Score 3: Strong technical projects showing initiative and complexity — but no leadership roles, no metrics, no external recognition.
  Score 4: Limited activities. Score 5: No notable extracurriculars.
  How to move up: Secure national-level recognition, lead larger teams, add published work or measurable user impact.

Mind (Scholarly Curiosity)
  Measures: Research, competitive academic wins, independent projects, faculty endorsement.
  Score 1: National academic competitions + faculty-mentored research + publications.
  Score 2: National competitions OR formal research with faculty endorsement.
  Score 3: Self-driven intellectual projects beyond coursework — but no national competitions, no publications, no professor endorsements.
  Score 4: Limited evidence of scholarly curiosity. Score 5: None.
  How to move up: Enter national competitions, pursue faculty-mentored research, publish in recognized venues.

Athletic
  Measures: Sports participation, varsity, competitions, physical discipline.
  Score 1: National/elite level athlete. Score 2: Varsity + competition wins.
  Score 3: Varsity or JV participation. Score 4: Club/recreational only.
  Score 5: No athletic participation documented.

Personality
  Measures: Resilience, empathy, leadership, authenticity, community contribution.
  Primarily assessed through personal essay — null score without a written response.
  Conversation signals (resilience, curiosity, values) can provide a preliminary read.
  Score 1: Exceptional story with clear values and demonstrated impact.
  Score 2: Compelling narrative with strong character signals.
  Score 3: Decent character signals but limited story depth.
  Score 4: Generic or unclear personality. Score 5: No signal.

Overall
  Holistic composite weighted toward strengths — anchored by strongest core criteria.
  NOT an average. A Score 1 requires Harvard-caliber performance across all core criteria.

──────────────────────────────────────────────────────────────
ENTREPRENEURSHIP
"Venture Talent is the differentiating criterion. Prospective interest from potential
users does not count. Paying customers, MRR, and engagement metrics are the only
signals that move the needle here."
──────────────────────────────────────────────────────────────

Skills & Talent
  Measures: Full-stack technical ability, domain knowledge, competition wins, internship credentials.
  Tier 1: Competition wins + proven traction + internship experience.
  Tier 2: Strong technical skills + some external validation.
  Tier 3–4: Capable builder — but no wins, traction, or external validation.
  Tier 5: Limited relevant skills.
  How to move up: Pursue relevant internships or competitions; acquire measurable traction.

Venture Talent
  Measures: Actual traction ONLY — paying customers, MRR, active users, engagement metrics.
  Prospective user interest and intent-to-subscribe do NOT count.
  Tier 1: Significant MRR, thousands of active users.
  Tier 2: Paying customers, measurable engagement.
  Tier 3: Functional MVP, some non-paying users or interest.
  Tier 4: MVP without users. Tier 5: Idea stage only.
  How to move up: Convert interested users to paying customers; track and share MRR and engagement metrics.

Commitment & Work Ethic
  Measures: Time invested weekly, months of sustained effort, iteration beyond MVP, trade-offs made.
  Tier 1: Full-time commitment, documented iteration history, explicit trade-offs made.
  Tier 2: Consistent part-time, multiple versions shipped.
  Tier 3: Technically advanced MVP — but no explicit time commitment stated, no iteration history.
  Tier 4: Brief or intermittent effort. Tier 5: Minimal time invested.
  How to move up: Document weekly hours and total months; describe prior versions; highlight trade-offs made to prioritize the venture.

──────────────────────────────────────────────────────────────
RESEARCH
"The ceiling without formal lab work or publications is Tier 3 regardless of subject
matter depth. Specificity is everything — named researchers, actual papers, and exact
methodologies separate Tier 2 from Tier 3."
──────────────────────────────────────────────────────────────

Scientific Depth & Understanding
  Measures: Specificity of knowledge — named labs, researchers, publications, mechanisms cited correctly.
  Tier 1: Can name specific labs, researchers, cite papers by title/author, and describe exact methodologies.
  Tier 2: Cites specific mechanisms and relevant publications accurately.
  Tier 3: Can discuss specific mechanisms — but names no specific labs or researchers.
  Tier 4: General subject knowledge, no specific citations. Tier 5: Surface-level only.
  How to move up: Name specific labs and researchers; expand on proposed methodologies in detail.

Prior Experience & Projects
  Measures: Formal lab work, publications, poster presentations, advanced coursework with research component.
  Tier 1: First-author publication or formal lab affiliation with tangible output.
  Tier 2: Formal lab work OR poster presentation at a recognized venue.
  Tier 3: High GPA, well-articulated research question, strong academic foundation — but no formal lab work, no publications.
  Tier 4: General interest but no structured work. Tier 5: No prior experience.
  How to move up: Engage in formal lab work or a research internship; submit a poster or paper.

Commitment & Learning
  Measures: Months of dedicated study, consistency of engagement, deepening involvement over time.
  Tier 1: Joined a lab, attending conferences, actively building community connections.
  Tier 2: Months of dedicated self-directed learning, clear research question, systematic approach.
  Tier 3: Several months of focused self-directed learning.
  Tier 4: Recent or sporadic interest. Tier 5: No sustained commitment.
  How to move up: Join a lab as volunteer or intern; attend workshops or conferences; build connections in the research community.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
