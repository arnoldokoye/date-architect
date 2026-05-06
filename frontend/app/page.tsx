"use client";

import { useState, useEffect } from "react";
import DateCard from "@/components/DateCard";
import type { DatePlanResponse } from "@/components/DateCard";

interface Persona {
  id: string;
  name: string;
  energy_level: number;
  conversation_style: string;
  interests: string[];
  values: string[];
  comfort_with_strangers: number;
  date_preference: string;
}

function PersonaProfileCard({ persona, label }: { persona: Persona; label: string }) {
  const DATE_PREF_LABELS: Record<string, string> = {
    low_pressure: "Low pressure",
    social: "Social",
    culinary: "Culinary",
    active: "Active",
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-rose-100 p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-sm font-semibold text-zinc-500 uppercase tracking-wide">{label}</div>
          <div className="text-lg font-bold text-zinc-900">{persona.name}</div>
        </div>
        <span className="text-sm bg-rose-100 text-rose-700 font-semibold px-2.5 py-1 rounded-full">
          {DATE_PREF_LABELS[persona.date_preference] ?? persona.date_preference}
        </span>
      </div>

      <div className="flex items-center gap-1.5 mb-3">
        <span className="text-sm text-zinc-500">Energy</span>
        <div className="flex gap-0.5">
          {[1, 2, 3, 4, 5].map((n) => (
            <div
              key={n}
              className={`w-3 h-3 rounded-full ${
                n <= persona.energy_level ? "bg-rose-400" : "bg-zinc-100"
              }`}
            />
          ))}
        </div>
        <span className="text-sm text-zinc-500 ml-1">{persona.conversation_style}</span>
      </div>

      <div className="mb-2">
        <div className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-1">Interests</div>
        <div className="flex flex-wrap gap-1">
          {persona.interests.map((i) => (
            <span key={i} className="bg-zinc-100 text-zinc-600 text-sm px-2 py-0.5 rounded-full">{i}</span>
          ))}
        </div>
      </div>

      <div>
        <div className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-1">Values</div>
        <div className="flex flex-wrap gap-1">
          {persona.values.map((v) => (
            <span key={v} className="bg-rose-50 text-rose-600 text-sm px-2 py-0.5 rounded-full">{v}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [personaA, setPersonaA] = useState("maya");
  const [personaB, setPersonaB] = useState("alex");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DatePlanResponse | null>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/personas`)
      .then((r) => r.json())
      .then(setPersonas);
  }, []);

  async function handleSubmit() {
    if (personaA === personaB) {
      setError("Please select two different people.");
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const resp = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/generate-date-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ persona_a_id: personaA, persona_b_id: personaB }),
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail ?? `Request failed (${resp.status})`);
      }
      setResult(await resp.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  const personaAName = personas.find((p) => p.id === personaA)?.name ?? personaA;
  const personaBName = personas.find((p) => p.id === personaB)?.name ?? personaB;

  return (
    <main className="min-h-screen bg-rose-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-rose-700 mb-2">Date Architect</h1>
          <p className="text-zinc-500 text-sm">Persona-aware date planning by Ditto AI</p>
        </div>

        {/* Selector card */}
        <div className="bg-white rounded-2xl shadow-sm border border-rose-100 p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-1">
                Person A
              </label>
              <select
                className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-base text-zinc-800 focus:outline-none focus:ring-2 focus:ring-rose-400"
                value={personaA}
                onChange={(e) => setPersonaA(e.target.value)}
              >
                {personas.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="hidden sm:flex items-center pb-2 text-zinc-300 font-light text-xl">
              ×
            </div>

            <div className="flex-1">
              <label className="block text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-1">
                Person B
              </label>
              <select
                className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-base text-zinc-800 focus:outline-none focus:ring-2 focus:ring-rose-400"
                value={personaB}
                onChange={(e) => setPersonaB(e.target.value)}
              >
                {personas.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="sm:flex-none w-full sm:w-auto rounded-lg bg-rose-600 text-white px-6 py-2 text-sm font-semibold hover:bg-rose-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Planning…" : "Find Our Date"}
            </button>
          </div>
        </div>

        {/* Profile cards */}
        {personas.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <PersonaProfileCard
              persona={personas.find((p) => p.id === personaA)!}
              label="Person A"
            />
            <PersonaProfileCard
              persona={personas.find((p) => p.id === personaB)!}
              label="Person B"
            />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 mb-6">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-center py-12 text-zinc-400 text-sm">
            <div className="animate-spin inline-block w-6 h-6 border-2 border-rose-300 border-t-rose-600 rounded-full mb-3" />
            <p>Generating your date plan… (~5s)</p>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <DateCard
            result={result}
            personaAName={personaAName}
            personaBName={personaBName}
          />
        )}
      </div>
    </main>
  );
}
