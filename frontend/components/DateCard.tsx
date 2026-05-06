export interface Venue {
  id: string;
  name: string;
  address: string;
  vibe_tags: string[];
  activity_type: string | null;
  price_tier: number;
  noise_level: number;
  intimacy_score: number;
  notes: string;
}

export interface RankedVenue {
  venue: Venue;
  score: number;
  score_breakdown: {
    energy_match: number;
    shared_activity: number;
    comfort_alignment: number;
    vibe_alignment: number;
  };
}

export interface PersonaCard {
  compatibility_story: string;
  venue_rationale: string;
  talking_points: string[];
  logistics: string;
}

interface CompatibilityBreakdown {
  energy_alignment: number;
  interest_overlap: number;
  values_alignment: number;
  vibe_compatibility: number;
}

interface PersonCompatibility {
  score: number;
  label: string;
  breakdown: CompatibilityBreakdown;
}

export interface DatePlanResponse {
  venue: RankedVenue;
  runner_up_venues: RankedVenue[];
  cards: {
    persona_a: PersonaCard;
    persona_b: PersonaCard;
  };
  compatibility: PersonCompatibility;
}

interface Props {
  result: DatePlanResponse;
  personaAName: string;
  personaBName: string;
}

const BREAKDOWN_DIM_LABELS: Record<string, string> = {
  energy_match: "energy match",
  shared_activity: "activity fit",
  comfort_alignment: "comfort fit",
  vibe_alignment: "vibe match",
};

function biggestGapDimension(
  winnerBreakdown: RankedVenue["score_breakdown"],
  runnerBreakdown: RankedVenue["score_breakdown"],
): { label: string; score: number } {
  const keys = Object.keys(winnerBreakdown) as Array<
    keyof typeof winnerBreakdown
  >;

  // Find the dimension where the runner-up lost the most ground vs the winner
  let bestKey = keys[0];
  let bestGap = winnerBreakdown[keys[0]] - runnerBreakdown[keys[0]];
  for (const key of keys.slice(1)) {
    const gap = winnerBreakdown[key] - runnerBreakdown[key];
    if (gap > bestGap) {
      bestGap = gap;
      bestKey = key;
    }
  }

  // Fallback: if runner-up tied or beat the winner on every dimension, show absolute weakest
  if (bestGap <= 0) {
    const [key] = (
      Object.entries(runnerBreakdown) as [keyof typeof runnerBreakdown, number][]
    ).sort(([, a], [, b]) => a - b)[0];
    bestKey = key;
  }

  return { label: BREAKDOWN_DIM_LABELS[bestKey] ?? bestKey, score: runnerBreakdown[bestKey] };
}

function CompatibilityBanner({
  compatibility,
  personaAName,
  personaBName,
}: {
  compatibility: PersonCompatibility;
  personaAName: string;
  personaBName: string;
}) {
  const dimLabels: Record<keyof CompatibilityBreakdown, string> = {
    energy_alignment: "Energy",
    interest_overlap: "Interests",
    values_alignment: "Values",
    vibe_compatibility: "Vibe",
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-rose-100 p-6">
      <div className="flex items-start justify-between gap-4 mb-1">
        <h2 className="text-lg font-bold text-zinc-900">
          {compatibility.label}
        </h2>
        <span className="shrink-0 inline-block bg-rose-100 text-rose-700 text-sm font-semibold px-3 py-1 rounded-full">
          {compatibility.score}/100
        </span>
      </div>
      <p className="text-base text-zinc-500 mb-4">
        {personaAName} × {personaBName}
      </p>
      <div className="grid grid-cols-4 gap-2 text-center">
        {(
          Object.keys(compatibility.breakdown) as Array<
            keyof CompatibilityBreakdown
          >
        ).map((key) => (
          <div key={key} className="bg-rose-50 rounded-lg p-2">
            <div className="text-sm text-zinc-500 mb-0.5">{dimLabels[key]}</div>
            <div className="text-base font-semibold text-rose-700">
              {compatibility.breakdown[key]}/25
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function PersonaCardPanel({ name, card }: { name: string; card: PersonaCard }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-rose-100 p-5">
      <h3 className="font-bold text-zinc-900 mb-4">{name}&rsquo;s Card</h3>
      <div className="space-y-4 text-base">
        <section>
          <div className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-1">
            Why you&rsquo;re a match
          </div>
          <p className="text-zinc-700 leading-relaxed">{card.compatibility_story}</p>
        </section>
        <section>
          <div className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-1">
            Why this venue
          </div>
          <p className="text-zinc-700 leading-relaxed">{card.venue_rationale}</p>
        </section>
        <section>
          <div className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-1">
            Talking points
          </div>
          <ul className="list-disc list-inside space-y-1 text-zinc-700">
            {card.talking_points.map((tp, i) => (
              <li key={i}>{tp}</li>
            ))}
          </ul>
        </section>
        <section>
          <div className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-1">
            Logistics
          </div>
          <p className="text-zinc-700 leading-relaxed">{card.logistics}</p>
        </section>
      </div>
    </div>
  );
}

export default function DateCard({ result, personaAName, personaBName }: Props) {
  const { venue: ranked, cards } = result;
  // alias for convenience
  const breakdown = ranked.score_breakdown;
  const venue = ranked.venue;

  const breakdownLabels: Record<string, string> = {
    energy_match: "Energy",
    shared_activity: "Activity",
    comfort_alignment: "Comfort",
    vibe_alignment: "Vibe",
  };

  return (
    <div className="space-y-4">
      {/* Compatibility banner */}
      <CompatibilityBanner
        compatibility={result.compatibility}
        personaAName={personaAName}
        personaBName={personaBName}
      />

      {/* Venue card */}
      <div className="bg-white rounded-2xl shadow-sm border border-rose-100 p-6">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div>
            <h2 className="text-xl font-bold text-zinc-900">{venue.name}</h2>
            <p className="text-sm text-zinc-500">{venue.address}</p>
          </div>
          <span className="shrink-0 inline-block bg-rose-100 text-rose-700 text-sm font-semibold px-3 py-1 rounded-full">
            {ranked.score}/100
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5 mb-4">
          {venue.vibe_tags.map((tag) => (
            <span
              key={tag}
              className="bg-zinc-100 text-zinc-600 text-xs px-2 py-0.5 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>

        <p className="text-sm text-zinc-500 mb-4">{venue.notes}</p>

        <div className="grid grid-cols-4 gap-2 text-center">
          {(Object.keys(breakdown) as Array<keyof typeof breakdown>).map(
            (key) => (
              <div key={key} className="bg-rose-50 rounded-lg p-2">
                <div className="text-sm text-zinc-500 mb-0.5">
                  {breakdownLabels[key] ?? key}
                </div>
                <div className="text-base font-semibold text-rose-700">
                  {breakdown[key]}/25
                </div>
              </div>
            )
          )}
        </div>
      </div>

      {/* Persona cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <PersonaCardPanel name={personaAName} card={cards.persona_a} />
        <PersonaCardPanel name={personaBName} card={cards.persona_b} />
      </div>

      {/* Runner-up venues */}
      {result.runner_up_venues.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-rose-100 p-4">
          <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-3">
            Also Considered
          </div>
          <div>
            {result.runner_up_venues.map((runnerUp, i) => {
              const weak = biggestGapDimension(result.venue.score_breakdown, runnerUp.score_breakdown);
              return (
                <div
                  key={runnerUp.venue.id}
                  className={`flex items-center justify-between py-3 ${
                    i < result.runner_up_venues.length - 1
                      ? "border-b border-zinc-100"
                      : ""
                  }`}
                >
                  <div>
                    <p className="text-base font-semibold text-zinc-800">
                      {runnerUp.venue.name}
                    </p>
                    <p className="text-sm text-zinc-500 mt-0.5">
                      Lost on: {weak.label} ({weak.score}/25)
                    </p>
                  </div>
                  <span className="shrink-0 ml-4 inline-block bg-zinc-100 text-zinc-600 text-xs font-semibold px-2.5 py-1 rounded-full">
                    {runnerUp.score}/100
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
