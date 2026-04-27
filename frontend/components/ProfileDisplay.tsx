'use client'

// ---- Types ---------------------------------------------------------------

type SubCriterion = { rating: number; rationale: string }
type SubCriterionScore = { score: number | null; rationale: string }

type Profile = {
  academic: {
    gpa?: number | null
    graduation_year?: number | null
    test_scores: { SAT?: number | null; ACT?: number | null }
    courses: string[]
  }
  skills: { technical: string[]; soft: string[] }
  interests: string[]
  goals: {
    college_targets: string[]
    career_direction: string
    research_interests: string[]
  }
  experience: { title: string; org: string; description: string }[]
  opportunity_ratings: {
    internship_match: {
      skills_and_talent: SubCriterion
      development_experience: SubCriterion
      work_ethic_and_output: SubCriterion
      overall_tier: number
      priority_actions: string[]
    }
    college_chance: {
      academic: SubCriterionScore
      extracurriculars: SubCriterionScore
      mind: SubCriterionScore
      athletic: SubCriterionScore
      personality: SubCriterionScore
      overall: number
      priority_actions: string[]
    }
    entrepreneurship: {
      skills_and_talent: SubCriterion
      venture_talent: SubCriterion
      commitment_and_work_ethic: SubCriterion
      overall_tier: number
      priority_actions: string[]
    }
    research: {
      scientific_depth_and_understanding: SubCriterion
      prior_experience_and_projects: SubCriterion
      commitment_and_learning: SubCriterion
      overall_tier: number
      priority_actions: string[]
    }
  }
}

// ---- Primitives ----------------------------------------------------------

function tierColors(value: number | null): { badge: string; bar: string } {
  if (value === null) return { badge: 'bg-zinc-800 text-zinc-500', bar: 'bg-zinc-700' }
  if (value <= 2) return { badge: 'bg-emerald-900/60 text-emerald-300', bar: 'bg-emerald-500' }
  if (value === 3) return { badge: 'bg-amber-900/50 text-amber-300', bar: 'bg-amber-500' }
  return { badge: 'bg-rose-900/50 text-rose-300', bar: 'bg-rose-500' }
}

function TierBadge({
  value,
  label,
  size = 'sm',
}: {
  value: number | null
  label?: string
  size?: 'sm' | 'lg'
}) {
  const { badge } = tierColors(value)
  const displayLabel = label ?? (value !== null ? `Tier ${value}` : 'N/A')
  return (
    <span
      className={`inline-block rounded-lg font-semibold ${badge} ${
        size === 'lg' ? 'px-4 py-1.5 text-base' : 'px-2.5 py-0.5 text-xs'
      }`}
    >
      {displayLabel}
    </span>
  )
}

function Tag({
  text,
  color = 'slate',
}: {
  text: string
  color?: 'slate' | 'violet' | 'emerald' | 'amber' | 'sky'
}) {
  const colorMap = {
    slate:   'bg-zinc-800 text-zinc-400',
    violet:  'bg-zinc-800 text-[#9d8fc0]',
    emerald: 'bg-emerald-900/50 text-emerald-300',
    amber:   'bg-amber-900/40 text-amber-300',
    sky:     'bg-sky-900/50 text-sky-300',
  }
  return (
    <span className={`inline-block rounded-lg px-2.5 py-1 text-xs font-medium ${colorMap[color]}`}>
      {text}
    </span>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 rounded-2xl p-6 border border-zinc-800">
      <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">{title}</h2>
      {children}
    </div>
  )
}

// ---- Criterion row inside an opportunity card ----------------------------

function CriterionRow({
  name,
  value,
  rationale,
  valueType = 'tier',
}: {
  name: string
  value: number | null
  rationale: string
  valueType?: 'tier' | 'score'
}) {
  const { bar } = tierColors(value)
  const displayLabel = value !== null ? `${valueType === 'score' ? 'Score' : 'Tier'} ${value}` : 'N/A'
  const pct = value !== null ? Math.round(((6 - value) / 5) * 100) : 0

  return (
    <div className="py-3 border-b border-zinc-800 last:border-0">
      <div className="flex items-center justify-between gap-3 mb-1.5">
        <span className="text-zinc-300 text-sm font-medium">{name}</span>
        <TierBadge value={value} label={displayLabel} />
      </div>
      <div className="w-full h-1 rounded-full bg-zinc-800 mb-2">
        <div className={`h-full rounded-full ${bar}`} style={{ width: `${pct}%` }} />
      </div>
      <p className="text-zinc-500 text-xs leading-relaxed">{rationale}</p>
    </div>
  )
}

// ---- Full opportunity area card ------------------------------------------

function OpportunityCard({
  title,
  axiom,
  overallValue,
  overallLabel,
  overallType,
  criteria,
  priorityActions,
}: {
  title: string
  axiom: string
  overallValue: number
  overallLabel: string
  overallType: 'tier' | 'score'
  criteria: { name: string; value: number | null; rationale: string; valueType?: 'tier' | 'score' }[]
  priorityActions: string[]
}) {
  return (
    <div className="bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="p-6 pb-4 border-b border-zinc-800">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-white font-semibold text-lg">{title}</h2>
            <p className="text-zinc-500 text-xs mt-1 leading-relaxed max-w-sm">{axiom}</p>
          </div>
          <div className="text-right shrink-0">
            <div className="text-zinc-500 text-xs mb-1">{overallLabel}</div>
            <TierBadge
              value={overallValue}
              label={`${overallType === 'score' ? 'Score' : 'Tier'} ${overallValue}`}
              size="lg"
            />
          </div>
        </div>
      </div>

      {/* Criteria */}
      <div className="px-6">
        {criteria.map((c) => (
          <CriterionRow
            key={c.name}
            name={c.name}
            value={c.value}
            rationale={c.rationale}
            valueType={c.valueType ?? overallType}
          />
        ))}
      </div>

      {/* Priority Actions */}
      {priorityActions.length > 0 && (
        <div className="px-6 pb-6 pt-4">
          <p className="text-zinc-500 text-xs font-semibold uppercase tracking-wider mb-2">
            Priority Actions
          </p>
          <ul className="space-y-1.5">
            {priorityActions.map((action, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                <span className="text-[#8b7aaa] mt-0.5 shrink-0">→</span>
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// ---- Main component ------------------------------------------------------

export default function ProfileDisplay({ profile }: { profile: Profile }) {
  const { academic, opportunity_ratings: opp } = profile

  if (!opp?.internship_match || !opp?.college_chance || !opp?.entrepreneurship || !opp?.research) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-zinc-400 text-sm mb-2">Profile data is incomplete.</p>
          <p className="text-zinc-600 text-xs">Please go back and regenerate the profile.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black px-4 py-10">
      <div className="max-w-4xl mx-auto space-y-5">

        {/* Header */}
        <div className="bg-zinc-900 rounded-2xl p-8 border border-zinc-800">
          <div className="inline-flex items-center gap-2 bg-zinc-800 border border-zinc-700 rounded-full px-3 py-1 mb-3">
            <span className="h-1.5 w-1.5 rounded-full bg-[#8b7aaa]" />
            <span className="text-[#8b7aaa] text-xs font-medium tracking-wide uppercase">
              Ultra Student Profile
            </span>
          </div>
          <h1 className="font-serif text-white text-2xl font-bold mb-1">Opportunity Assessment</h1>
          <p className="text-zinc-400 text-sm">
            Rubric-based ratings across four areas — each tier reflects external validation, not
            self-reported intent.
          </p>

          {/* Quick overview tiles */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
            {[
              { label: 'Internship Match', value: opp.internship_match.overall_tier, type: 'tier' as const },
              { label: 'College Chance',   value: opp.college_chance.overall,        type: 'score' as const },
              { label: 'Entrepreneurship', value: opp.entrepreneurship.overall_tier, type: 'tier' as const },
              { label: 'Research',         value: opp.research.overall_tier,         type: 'tier' as const },
            ].map(({ label, value, type }) => (
              <div key={label} className="bg-zinc-800 rounded-xl p-4 text-center">
                <p className="text-zinc-500 text-xs mb-2">{label}</p>
                <TierBadge
                  value={value}
                  label={`${type === 'score' ? 'Score' : 'Tier'} ${value}`}
                  size="lg"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Internship Match */}
        <OpportunityCard
          title="Internship Match"
          axiom="Tier is determined by external validation and demonstrated output — shipping something real that others use is the primary signal."
          overallValue={opp.internship_match.overall_tier}
          overallLabel="Overall Tier"
          overallType="tier"
          criteria={[
            {
              name: 'Skills & Talent',
              value: opp.internship_match.skills_and_talent.rating,
              rationale: opp.internship_match.skills_and_talent.rationale,
            },
            {
              name: 'Development Experience',
              value: opp.internship_match.development_experience.rating,
              rationale: opp.internship_match.development_experience.rationale,
            },
            {
              name: 'Work Ethic & Output',
              value: opp.internship_match.work_ethic_and_output.rating,
              rationale: opp.internship_match.work_ethic_and_output.rationale,
            },
          ]}
          priorityActions={opp.internship_match.priority_actions}
        />

        {/* College Chance */}
        <OpportunityCard
          title="College Chance"
          axiom="Overall score is not an average — it weights strengths and ignores weak areas. All Score 1s got into Harvard; over 50% of Score 2s did."
          overallValue={opp.college_chance.overall}
          overallLabel="Overall Score"
          overallType="score"
          criteria={[
            {
              name: 'Academic',
              value: opp.college_chance.academic.score,
              rationale: opp.college_chance.academic.rationale,
              valueType: 'score',
            },
            {
              name: 'Extracurriculars',
              value: opp.college_chance.extracurriculars.score,
              rationale: opp.college_chance.extracurriculars.rationale,
              valueType: 'score',
            },
            {
              name: 'Mind',
              value: opp.college_chance.mind.score,
              rationale: opp.college_chance.mind.rationale,
              valueType: 'score',
            },
            {
              name: 'Athletic',
              value: opp.college_chance.athletic.score,
              rationale: opp.college_chance.athletic.rationale,
              valueType: 'score',
            },
            {
              name: 'Personality',
              value: opp.college_chance.personality.score,
              rationale: opp.college_chance.personality.rationale,
              valueType: 'score',
            },
          ]}
          priorityActions={opp.college_chance.priority_actions}
        />

        {/* Entrepreneurship */}
        <OpportunityCard
          title="Entrepreneurship"
          axiom="Venture Talent is the differentiating criterion. Prospective user interest does not count — only paying customers, MRR, and engagement metrics move the needle."
          overallValue={opp.entrepreneurship.overall_tier}
          overallLabel="Overall Tier"
          overallType="tier"
          criteria={[
            {
              name: 'Skills & Talent',
              value: opp.entrepreneurship.skills_and_talent.rating,
              rationale: opp.entrepreneurship.skills_and_talent.rationale,
            },
            {
              name: 'Venture Talent',
              value: opp.entrepreneurship.venture_talent.rating,
              rationale: opp.entrepreneurship.venture_talent.rationale,
            },
            {
              name: 'Commitment & Work Ethic',
              value: opp.entrepreneurship.commitment_and_work_ethic.rating,
              rationale: opp.entrepreneurship.commitment_and_work_ethic.rationale,
            },
          ]}
          priorityActions={opp.entrepreneurship.priority_actions}
        />

        {/* Research */}
        <OpportunityCard
          title="Research"
          axiom="The ceiling without formal lab work or publications is Tier 3 regardless of subject matter depth. Named researchers, actual papers, and exact methodologies separate Tier 2 from Tier 3."
          overallValue={opp.research.overall_tier}
          overallLabel="Overall Tier"
          overallType="tier"
          criteria={[
            {
              name: 'Scientific Depth & Understanding',
              value: opp.research.scientific_depth_and_understanding.rating,
              rationale: opp.research.scientific_depth_and_understanding.rationale,
            },
            {
              name: 'Prior Experience & Projects',
              value: opp.research.prior_experience_and_projects.rating,
              rationale: opp.research.prior_experience_and_projects.rationale,
            },
            {
              name: 'Commitment & Learning',
              value: opp.research.commitment_and_learning.rating,
              rationale: opp.research.commitment_and_learning.rationale,
            },
          ]}
          priorityActions={opp.research.priority_actions}
        />

        {/* Two-column: Academic + Goals */}
        <div className="grid md:grid-cols-2 gap-5">

          {/* Academic */}
          <Section title="Academic Profile">
            <div className="flex gap-6 mb-4">
              {academic.gpa && (
                <div>
                  <p className="text-2xl font-bold text-white">{academic.gpa}</p>
                  <p className="text-zinc-500 text-xs">GPA</p>
                </div>
              )}
              {academic.test_scores?.SAT && (
                <div>
                  <p className="text-2xl font-bold text-white">{academic.test_scores.SAT}</p>
                  <p className="text-zinc-500 text-xs">SAT</p>
                </div>
              )}
              {academic.test_scores?.ACT && (
                <div>
                  <p className="text-2xl font-bold text-white">{academic.test_scores.ACT}</p>
                  <p className="text-zinc-500 text-xs">ACT</p>
                </div>
              )}
              {academic.graduation_year && (
                <div>
                  <p className="text-2xl font-bold text-white">{academic.graduation_year}</p>
                  <p className="text-zinc-500 text-xs">Grad Year</p>
                </div>
              )}
            </div>
            {academic.courses.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {academic.courses.map((c) => (
                  <Tag key={c} text={c} color="sky" />
                ))}
              </div>
            )}
          </Section>

          {/* Goals & Interests */}
          <Section title="Goals & Interests">
            <div className="space-y-3">
              <div>
                <p className="text-zinc-500 text-xs mb-1">Career Direction</p>
                <p className="text-zinc-300 text-sm">{profile.goals.career_direction}</p>
              </div>
              {profile.goals.college_targets.length > 0 && (
                <div>
                  <p className="text-zinc-500 text-xs mb-1.5">Target Schools</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.goals.college_targets.map((s) => (
                      <Tag key={s} text={s} color="amber" />
                    ))}
                  </div>
                </div>
              )}
              {profile.interests.length > 0 && (
                <div>
                  <p className="text-zinc-500 text-xs mb-1.5">Interests</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.interests.map((r) => (
                      <Tag key={r} text={r} color="violet" />
                    ))}
                  </div>
                </div>
              )}
              {profile.goals.research_interests.length > 0 && (
                <div>
                  <p className="text-zinc-500 text-xs mb-1.5">Research Interests</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.goals.research_interests.map((r) => (
                      <Tag key={r} text={r} color="sky" />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Section>

          {/* Skills */}
          <Section title="Skills">
            <div className="space-y-3">
              {profile.skills.technical.length > 0 && (
                <div>
                  <p className="text-zinc-500 text-xs mb-1.5">Technical</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.skills.technical.map((s) => (
                      <Tag key={s} text={s} color="violet" />
                    ))}
                  </div>
                </div>
              )}
              {profile.skills.soft.length > 0 && (
                <div>
                  <p className="text-zinc-500 text-xs mb-1.5">Soft Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.skills.soft.map((s) => (
                      <Tag key={s} text={s} color="slate" />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Section>

          {/* Experience */}
          {profile.experience.length > 0 && (
            <Section title="Experience">
              <div className="space-y-4">
                {profile.experience.map((w, i) => (
                  <div key={i} className="border-l-2 border-zinc-700 pl-4">
                    <p className="text-zinc-100 font-medium text-sm">{w.title}</p>
                    <p className="text-zinc-500 text-xs mb-1">{w.org}</p>
                    <p className="text-zinc-400 text-xs leading-relaxed">{w.description}</p>
                  </div>
                ))}
              </div>
            </Section>
          )}
        </div>

      </div>
    </div>
  )
}
