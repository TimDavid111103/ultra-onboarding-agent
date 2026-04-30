'use client'

// ---- Types ---------------------------------------------------------------

type SubcategoryContext = { confidence: number; context: string }

type InternshipMatchSection = {
  confidence: number
  summary: string
  skills_and_talent: SubcategoryContext
  development_experience: SubcategoryContext
  work_ethic_and_output: SubcategoryContext
  key_points: string[]
}

type CollegeChanceSection = {
  confidence: number
  summary: string
  academic: SubcategoryContext
  extracurriculars: SubcategoryContext
  mind: SubcategoryContext
  athletic: SubcategoryContext
  personality: SubcategoryContext
  key_points: string[]
}

type EntrepreneurshipSection = {
  confidence: number
  summary: string
  skills_and_talent: SubcategoryContext
  venture_talent: SubcategoryContext
  commitment_and_work_ethic: SubcategoryContext
  key_points: string[]
}

type ResearchSection = {
  confidence: number
  summary: string
  scientific_depth_and_understanding: SubcategoryContext
  prior_experience_and_projects: SubcategoryContext
  commitment_and_learning: SubcategoryContext
  key_points: string[]
}

type Profile = {
  skills: { technical: string[]; soft: string[] }
  interests: string[]
  goals: {
    college_targets: string[]
    career_direction: string
    research_interests: string[]
  }
  opportunity_ratings: {
    internship_match: InternshipMatchSection
    college_chance: CollegeChanceSection
    entrepreneurship: EntrepreneurshipSection
    research: ResearchSection
  }
}

// ---- Primitives ----------------------------------------------------------

function confidenceColors(score: number) {
  if (score >= 80) return { badge: 'bg-emerald-900/50 text-emerald-300', bar: 'bg-emerald-500' }
  if (score >= 50) return { badge: 'bg-yellow-900/40 text-yellow-400',   bar: 'bg-yellow-500'  }
  return                  { badge: 'bg-rose-900/40 text-rose-300',       bar: 'bg-rose-500'    }
}

function ConfidenceBadge({ score }: { score: number }) {
  const { badge } = confidenceColors(score)
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${badge}`}>
      {score}% signal
    </span>
  )
}

function Tag({
  text,
  color = 'slate',
}: {
  text: string
  color?: 'slate' | 'violet' | 'emerald' | 'amber' | 'sky' | 'rose'
}) {
  const colorMap = {
    slate:   'bg-zinc-800 text-zinc-400',
    violet:  'bg-zinc-800 text-[#9d8fc0]',
    emerald: 'bg-emerald-900/50 text-emerald-300',
    amber:   'bg-amber-900/40 text-amber-300',
    sky:     'bg-zinc-800 text-sky-300',
    rose:    'bg-zinc-800 text-rose-300',
  }
  return (
    <span className={`inline-block rounded-lg px-2.5 py-1 text-xs font-medium ${colorMap[color]}`}>
      {text}
    </span>
  )
}

function SubcategoryCard({ name, confidence, context }: { name: string; confidence: number; context: string }) {
  const { badge } = confidenceColors(confidence)
  return (
    <div className="bg-zinc-800/60 rounded-xl border border-zinc-700/50 p-4">
      <div className="flex items-center justify-between gap-2 mb-2">
        <p className="text-zinc-500 text-xs font-semibold uppercase tracking-wider">{name}</p>
        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${badge}`}>
          {confidence}%
        </span>
      </div>
      <p className="text-zinc-300 text-sm leading-relaxed">{context}</p>
    </div>
  )
}

function VerticalCard({
  title,
  confidence,
  summary,
  subcategories,
  keyPoints,
}: {
  title: string
  confidence: number
  summary: string
  subcategories: { name: string; confidence: number; context: string }[]
  keyPoints: string[]
}) {
  const { bar } = confidenceColors(confidence)
  return (
    <div className="bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="px-6 pt-6 pb-4 border-b border-zinc-800">
        <div className="flex items-start justify-between gap-4 mb-3">
          <h2 className="text-white font-semibold text-lg">{title}</h2>
          <ConfidenceBadge score={confidence} />
        </div>
        {/* Confidence bar */}
        <div className="w-full h-0.5 rounded-full bg-zinc-800">
          <div className={`h-full rounded-full ${bar} transition-all`} style={{ width: `${confidence}%` }} />
        </div>
      </div>

      {/* Summary */}
      <div className="px-6 pt-5 pb-4">
        <p className="text-zinc-400 text-sm leading-relaxed">{summary}</p>
      </div>

      {/* Subcategories */}
      <div className="px-6 pb-5">
        <div className="flex flex-col gap-3">
          {subcategories.map((s) => (
            <SubcategoryCard key={s.name} name={s.name} confidence={s.confidence} context={s.context} />
          ))}
        </div>
      </div>

      {/* Key Points */}
      {keyPoints.length > 0 && (
        <div className="px-6 pb-6 pt-1 border-t border-zinc-800">
          <p className="text-zinc-500 text-xs font-semibold uppercase tracking-wider mb-3 mt-4">
            Key Points
          </p>
          <ul className="space-y-2">
            {keyPoints.map((pt, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                <span className="text-[#8b7aaa] mt-0.5 shrink-0">→</span>
                {pt}
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
  const { skills, interests, goals, opportunity_ratings: opp } = profile

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

        {/* Internship Match */}
        <VerticalCard
          title="Internship Match"
          confidence={opp.internship_match.confidence}
          summary={opp.internship_match.summary}
          subcategories={[
            { name: 'Skills & Talent',        confidence: opp.internship_match.skills_and_talent.confidence,        context: opp.internship_match.skills_and_talent.context },
            { name: 'Development Experience', confidence: opp.internship_match.development_experience.confidence,   context: opp.internship_match.development_experience.context },
            { name: 'Work Ethic & Output',    confidence: opp.internship_match.work_ethic_and_output.confidence,    context: opp.internship_match.work_ethic_and_output.context },
          ]}
          keyPoints={opp.internship_match.key_points}
        />

        {/* College Chance */}
        <VerticalCard
          title="College Chance"
          confidence={opp.college_chance.confidence}
          summary={opp.college_chance.summary}
          subcategories={[
            { name: 'Academic',         confidence: opp.college_chance.academic.confidence,         context: opp.college_chance.academic.context },
            { name: 'Extracurriculars', confidence: opp.college_chance.extracurriculars.confidence, context: opp.college_chance.extracurriculars.context },
            { name: 'Mind',             confidence: opp.college_chance.mind.confidence,             context: opp.college_chance.mind.context },
            { name: 'Athletic',         confidence: opp.college_chance.athletic.confidence,         context: opp.college_chance.athletic.context },
            { name: 'Personality',      confidence: opp.college_chance.personality.confidence,      context: opp.college_chance.personality.context },
          ]}
          keyPoints={opp.college_chance.key_points}
        />

        {/* Entrepreneurship */}
        <VerticalCard
          title="Entrepreneurship"
          confidence={opp.entrepreneurship.confidence}
          summary={opp.entrepreneurship.summary}
          subcategories={[
            { name: 'Skills & Talent',         confidence: opp.entrepreneurship.skills_and_talent.confidence,         context: opp.entrepreneurship.skills_and_talent.context },
            { name: 'Venture Talent',          confidence: opp.entrepreneurship.venture_talent.confidence,            context: opp.entrepreneurship.venture_talent.context },
            { name: 'Commitment & Work Ethic', confidence: opp.entrepreneurship.commitment_and_work_ethic.confidence, context: opp.entrepreneurship.commitment_and_work_ethic.context },
          ]}
          keyPoints={opp.entrepreneurship.key_points}
        />

        {/* Research */}
        <VerticalCard
          title="Research"
          confidence={opp.research.confidence}
          summary={opp.research.summary}
          subcategories={[
            { name: 'Scientific Depth',      confidence: opp.research.scientific_depth_and_understanding.confidence, context: opp.research.scientific_depth_and_understanding.context },
            { name: 'Prior Experience',      confidence: opp.research.prior_experience_and_projects.confidence,      context: opp.research.prior_experience_and_projects.context },
            { name: 'Commitment & Learning', confidence: opp.research.commitment_and_learning.confidence,            context: opp.research.commitment_and_learning.context },
          ]}
          keyPoints={opp.research.key_points}
        />

        {/* Skills / Goals / Interests */}
        <div className="grid md:grid-cols-3 gap-5">

          <div className="bg-zinc-900 rounded-2xl p-5 border border-zinc-800">
            <p className="text-zinc-500 text-xs font-semibold uppercase tracking-wider mb-3">Skills</p>
            <div className="space-y-3">
              {skills.technical.length > 0 && (
                <div>
                  <p className="text-zinc-600 text-xs mb-1.5">Technical</p>
                  <div className="flex flex-wrap gap-1.5">
                    {skills.technical.map((s) => <Tag key={s} text={s} color="violet" />)}
                  </div>
                </div>
              )}
              {skills.soft.length > 0 && (
                <div>
                  <p className="text-zinc-600 text-xs mb-1.5">Soft Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {skills.soft.map((s) => <Tag key={s} text={s} color="rose" />)}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="bg-zinc-900 rounded-2xl p-5 border border-zinc-800">
            <p className="text-zinc-500 text-xs font-semibold uppercase tracking-wider mb-3">Goals</p>
            <div className="space-y-3">
              {goals.career_direction && (
                <div>
                  <p className="text-zinc-600 text-xs mb-1">Career Direction</p>
                  <p className="text-zinc-300 text-sm leading-relaxed">{goals.career_direction}</p>
                </div>
              )}
              {goals.college_targets.length > 0 && (
                <div>
                  <p className="text-zinc-600 text-xs mb-1.5">Target Schools</p>
                  <div className="flex flex-wrap gap-1.5">
                    {goals.college_targets.map((s) => <Tag key={s} text={s} color="emerald" />)}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="bg-zinc-900 rounded-2xl p-5 border border-zinc-800">
            <p className="text-zinc-500 text-xs font-semibold uppercase tracking-wider mb-3">Interests</p>
            <div className="space-y-3">
              {interests.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {interests.map((i) => <Tag key={i} text={i} color="violet" />)}
                </div>
              )}
              {goals.research_interests.length > 0 && (
                <div>
                  <p className="text-zinc-600 text-xs mb-1.5">Research</p>
                  <div className="flex flex-wrap gap-1.5">
                    {goals.research_interests.map((r) => <Tag key={r} text={r} color="sky" />)}
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  )
}
