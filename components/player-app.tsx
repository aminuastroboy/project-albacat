'use client'

import Image from 'next/image'
import { useEffect, useMemo, useRef, useState } from 'react'
import catalog from '@/data/catalog.json'
import team from '@/data/team.json'

type Lecture = {
  id: string
  title: string
  author: string
  series: string
  topic: string
  sessionNumber: number
  language: string
  duration: string
  date: string
  fileId: string
  description: string
  tags: string[]
  transcript?: string
}

type TeamMember = {
  name: string
  role: string
  organization?: string
  bio?: string
}

const lectures = catalog as Lecture[]
const teamData = team as {
  team_name: string
  mission: string
  contact?: { email?: string; phone?: string }
  members: TeamMember[]
}

const driveAudio = (fileId: string) =>
  `https://drive.google.com/uc?export=download&id=${fileId}`

const driveDownload = (fileId: string) =>
  `https://drive.google.com/uc?export=download&id=${fileId}`

export default function PlayerApp() {
  const [query, setQuery] = useState('')
  const [selectedTopic, setSelectedTopic] = useState('All')
  const [selectedSeries, setSelectedSeries] = useState('All')
  const [selectedId, setSelectedId] = useState<string>(lectures[0]?.id ?? '')
  const [showTeam, setShowTeam] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  useEffect(() => {
    const saved = window.localStorage.getItem('albacat:selectedId')
    if (saved) setSelectedId(saved)
  }, [])

  useEffect(() => {
    if (selectedId) window.localStorage.setItem('albacat:selectedId', selectedId)
  }, [selectedId])

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.load()
      void audioRef.current.play().catch(() => {})
    }
  }, [selectedId])

  const topics = useMemo(
    () => ['All', ...Array.from(new Set(lectures.map((x) => x.topic))).sort()],
    []
  )

  const seriesOptions = useMemo(
    () => ['All', ...Array.from(new Set(lectures.map((x) => x.series))).sort()],
    []
  )

  const filtered = useMemo(() => {
    return lectures
      .filter((item) => {
        if (selectedTopic !== 'All' && item.topic !== selectedTopic) return false
        if (selectedSeries !== 'All' && item.series !== selectedSeries) return false

        const haystack = [
          item.title,
          item.author,
          item.series,
          item.topic,
          item.description,
          item.transcript ?? '',
          ...(item.tags ?? []),
        ]
          .join(' ')
          .toLowerCase()

        return haystack.includes(query.toLowerCase())
      })
      .sort((a, b) => a.sessionNumber - b.sessionNumber)
  }, [query, selectedTopic, selectedSeries])

  const current = lectures.find((x) => x.id === selectedId) ?? filtered[0] ?? lectures[0]

  const currentSeries = useMemo(() => {
    if (!current) return []
    return lectures
      .filter((x) => x.series === current.series)
      .sort((a, b) => a.sessionNumber - b.sessionNumber)
  }, [current])

  const idx = currentSeries.findIndex((x) => x.id === current?.id)
  const prev = idx > 0 ? currentSeries[idx - 1] : null
  const next = idx >= 0 && idx < currentSeries.length - 1 ? currentSeries[idx + 1] : null

  return (
    <main className="min-h-screen px-4 py-5 md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="alb-card mb-6 rounded-[28px] p-5 md:p-7">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-3xl space-y-3">
              <div className="flex items-center gap-3">
                <div className="relative h-12 w-12 overflow-hidden rounded-2xl border border-white/10 bg-white/5">
                  <Image src="/logo.png" alt="Astrovia Systems" fill className="object-contain p-1" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.25em] text-sky-300">
                    Astrovia Systems
                  </p>
                  <p className="alb-muted text-sm">Next.js + Tailwind for Vercel</p>
                </div>
              </div>
              <h1 className="text-3xl font-bold leading-tight md:text-5xl">Project ALBACAT</h1>
              <p className="alb-muted text-sm leading-7 md:text-base">
                A cleaner Islamic history audio platform for Albani Zaria. Click any lecture and it starts in the native audio player automatically.
              </p>
              <div className="alb-muted flex flex-wrap gap-4 text-sm">
                <span>Email: {teamData.contact?.email}</span>
                <span>Phone: {teamData.contact?.phone}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <StatCard label="Lectures" value={String(lectures.length)} />
              <StatCard label="Series" value={String(new Set(lectures.map((x) => x.series)).size)} />
              <StatCard label="Topics" value={String(new Set(lectures.map((x) => x.topic)).size)} />
              <StatCard label="R&D Team" value={String(teamData.members.length)} />
            </div>
          </div>
        </header>

        <section className="mb-6 grid gap-6 lg:grid-cols-[280px_1fr]">
          <aside className="alb-card rounded-[28px] p-4 md:p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">Filters</p>
            <h2 className="mt-1 text-xl font-semibold">Search the library</h2>
            <div className="mt-4 space-y-4">
              <input
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none placeholder:text-slate-400"
                placeholder="Search lectures, tags, transcript..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <select
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none"
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
              >
                {topics.map((topic) => (
                  <option key={topic} value={topic} className="bg-slate-900">
                    {topic}
                  </option>
                ))}
              </select>
              <select
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none"
                value={selectedSeries}
                onChange={(e) => setSelectedSeries(e.target.value)}
              >
                {seriesOptions.map((series) => (
                  <option key={series} value={series} className="bg-slate-900">
                    {series}
                  </option>
                ))}
              </select>
              <button
                className="w-full rounded-2xl bg-sky-400 px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-sky-300"
                onClick={() => setShowTeam((v) => !v)}
              >
                {showTeam ? 'Hide R&D Team' : 'Show R&D Team'}
              </button>
            </div>
          </aside>

          <div className="space-y-6">
            <section className="grid gap-6 xl:grid-cols-[1fr_380px]">
              <div className="alb-card rounded-[28px] p-4 md:p-5">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div className="space-y-2">
                    <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">
                      Now playing
                    </p>
                    {current ? (
                      <>
                        <h2 className="text-2xl font-semibold md:text-3xl">{current.title}</h2>
                        <p className="alb-muted text-sm">
                          {current.author} • {current.series} • Session {current.sessionNumber}
                        </p>
                        <p className="alb-muted max-w-3xl text-sm leading-7">
                          {current.description}
                        </p>
                      </>
                    ) : (
                      <p className="alb-muted text-sm">Select a lecture to begin playback.</p>
                    )}
                  </div>

                  {current ? (
                    <div className="flex flex-wrap gap-2">
                      <button
                        className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10 disabled:opacity-40"
                        onClick={() => prev && setSelectedId(prev.id)}
                        disabled={!prev}
                      >
                        Previous
                      </button>
                      <button
                        className="rounded-xl bg-sky-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
                        onClick={() => audioRef.current?.play()}
                      >
                        Play
                      </button>
                      <button
                        className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10 disabled:opacity-40"
                        onClick={() => next && setSelectedId(next.id)}
                        disabled={!next}
                      >
                        Next
                      </button>
                      <a
                        href={driveDownload(current.fileId)}
                        className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10"
                      >
                        Download
                      </a>
                    </div>
                  ) : null}
                </div>

                <div className="mt-5 rounded-[24px] border border-white/10 bg-black/20 p-4">
                  {current ? (
                    <audio ref={audioRef} controls autoPlay className="w-full" key={current.fileId}>
                      <source src={driveAudio(current.fileId)} type="audio/mpeg" />
                      Your browser does not support audio playback.
                    </audio>
                  ) : (
                    <div className="flex h-20 items-center justify-center text-sm text-slate-400">
                      No lecture selected
                    </div>
                  )}
                </div>

                {current?.transcript ? (
                  <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-sm font-semibold text-white">Transcript excerpt</p>
                    <p className="alb-muted mt-2 text-sm leading-7">{current.transcript}</p>
                  </div>
                ) : null}
              </div>

              <div className="alb-card rounded-[28px] p-4 md:p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">
                  Series playlist
                </p>
                <div className="mt-4 space-y-3">
                  {currentSeries.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setSelectedId(item.id)}
                      className={`w-full rounded-2xl border px-4 py-4 text-left ${
                        item.id === current?.id
                          ? 'border-sky-300/35 bg-sky-400/10'
                          : 'border-white/10 bg-white/5 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-semibold">Session {item.sessionNumber}</p>
                          <p className="alb-muted text-sm">{item.title}</p>
                        </div>
                        <span className="alb-muted text-xs">{item.duration}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </section>

            {showTeam ? (
              <section className="alb-card rounded-[28px] p-5 md:p-6">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">
                  Research & Development
                </p>
                <h2 className="mt-2 text-2xl font-semibold">{teamData.team_name}</h2>
                <p className="alb-muted mt-3 text-sm leading-7">{teamData.mission}</p>
                <div className="mt-6 grid gap-4 md:grid-cols-2">
                  {teamData.members.map((member) => (
                    <div key={member.name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <h3 className="text-lg font-semibold">{member.name}</h3>
                      <p className="alb-muted text-sm">{member.role}</p>
                      {member.organization ? (
                        <p className="alb-muted mt-1 text-sm">{member.organization}</p>
                      ) : null}
                      {member.bio ? <p className="alb-muted mt-3 text-sm">{member.bio}</p> : null}
                    </div>
                  ))}
                </div>
              </section>
            ) : null}

            <section>
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">
                    Browse lectures
                  </p>
                  <h2 className="text-2xl font-semibold">Catalog</h2>
                </div>
                <p className="alb-muted text-sm">{filtered.length} result(s)</p>
              </div>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {filtered.map((item) => (
                  <LectureCard
                    key={item.id}
                    item={item}
                    active={item.id === current?.id}
                    onPlay={() => setSelectedId(item.id)}
                  />
                ))}
              </div>
            </section>
          </div>
        </section>
      </div>
    </main>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
      <p className="alb-muted text-xs uppercase tracking-[0.18em]">{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  )
}

function LectureCard({
  item,
  onPlay,
  active,
}: {
  item: Lecture
  onPlay: () => void
  active?: boolean
}) {
  return (
    <div className={`alb-card rounded-[28px] p-5 ${active ? 'ring-2 ring-sky-300/35' : ''}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-300">
            {item.series}
          </p>
          <h3 className="mt-2 text-xl font-semibold">{item.title}</h3>
        </div>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs">
          {item.duration}
        </span>
      </div>
      <p className="alb-muted mt-3 text-sm">
        {item.author} • {item.topic} • Session {item.sessionNumber}
      </p>
      <p className="alb-muted mt-4 text-sm leading-7">{item.description}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {item.tags?.map((tag) => (
          <span key={tag} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">
            {tag}
          </span>
        ))}
      </div>
      <div className="mt-5 flex gap-3">
        <button
          className="rounded-xl bg-sky-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
          onClick={onPlay}
        >
          Play
        </button>
        <a
          href={driveDownload(item.fileId)}
          className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10"
        >
          Download
        </a>
      </div>
    </div>
  )
}
