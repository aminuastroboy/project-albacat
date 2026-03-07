'use client'

import { useEffect, useMemo, useState } from 'react'
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

const drivePreview = (fileId: string) =>
  `https://drive.google.com/file/d/${fileId}/preview`

const driveDownload = (fileId: string) =>
  `https://drive.google.com/uc?export=download&id=${fileId}`

export default function AlbacatApp() {
  const [query, setQuery] = useState('')
  const [selectedTopic, setSelectedTopic] = useState('All')
  const [selectedSeries, setSelectedSeries] = useState('All')
  const [selectedId, setSelectedId] = useState<string>(lectures[0]?.id ?? '')
  const [tab, setTab] = useState<'browse' | 'playlist' | 'transcripts' | 'team'>('browse')

  useEffect(() => {
    const saved = window.localStorage.getItem('albacat:selectedId')
    if (saved) setSelectedId(saved)
  }, [])

  useEffect(() => {
    if (selectedId) window.localStorage.setItem('albacat:selectedId', selectedId)
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
  }, [query, selectedSeries, selectedTopic])

  const current = lectures.find((x) => x.id === selectedId) ?? filtered[0] ?? lectures[0]

  const currentSeries = useMemo(() => {
    if (!current) return []
    return lectures
      .filter((x) => x.series === current.series)
      .sort((a, b) => a.sessionNumber - b.sessionNumber)
  }, [current])

  const currentIndex = currentSeries.findIndex((x) => x.id === current?.id)
  const previous = currentIndex > 0 ? currentSeries[currentIndex - 1] : null
  const next = currentIndex >= 0 && currentIndex < currentSeries.length - 1 ? currentSeries[currentIndex + 1] : null

  return (
    <main className="min-h-screen px-4 py-6 md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="albacat-card mb-6 rounded-3xl p-5 md:p-6">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="space-y-2">
              <p className="text-sm font-medium uppercase tracking-[0.25em] text-sky-300">
                Astrovia Systems
              </p>
              <h1 className="text-3xl font-bold md:text-4xl">Project ALBACAT</h1>
              <p className="albacat-muted max-w-3xl text-sm md:text-base">
                Islamic history audio library for Albani Zaria. Built with Next.js, Tailwind,
                and optimized for Vercel deployment.
              </p>
              <div className="albacat-muted flex flex-wrap gap-4 text-sm">
                <span>Email: {teamData.contact?.email}</span>
                <span>Phone: {teamData.contact?.phone}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <StatCard label="Lectures" value={String(lectures.length)} />
              <StatCard
                label="Series"
                value={String(new Set(lectures.map((x) => x.series)).size)}
              />
              <StatCard
                label="Topics"
                value={String(new Set(lectures.map((x) => x.topic)).size)}
              />
              <StatCard label="R&D Team" value={String(teamData.members.length)} />
            </div>
          </div>
        </header>

        <section className="mb-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="albacat-card rounded-3xl p-5 md:p-6">
            <div className="mb-4 flex flex-col gap-2">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">
                Search & Browse
              </p>
              <h2 className="text-2xl font-semibold">Find lectures fast</h2>
              <p className="albacat-muted text-sm">
                Search across titles, descriptions, tags, and transcript excerpts.
              </p>
            </div>

            <div className="grid gap-3 md:grid-cols-[2fr_1fr_1fr]">
              <input
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none ring-0 placeholder:text-slate-400"
                placeholder="Search lectures, transcript text, topics..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <select
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none"
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
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none"
                value={selectedSeries}
                onChange={(e) => setSelectedSeries(e.target.value)}
              >
                {seriesOptions.map((series) => (
                  <option key={series} value={series} className="bg-slate-900">
                    {series}
                  </option>
                ))}
              </select>
            </div>

            <div className="mt-5 flex flex-wrap gap-3">
              <TabButton active={tab === 'browse'} onClick={() => setTab('browse')}>
                Browse
              </TabButton>
              <TabButton active={tab === 'playlist'} onClick={() => setTab('playlist')}>
                Series Playlist
              </TabButton>
              <TabButton active={tab === 'transcripts'} onClick={() => setTab('transcripts')}>
                Transcripts
              </TabButton>
              <TabButton active={tab === 'team'} onClick={() => setTab('team')}>
                R&D Team
              </TabButton>
            </div>
          </div>

          <div className="albacat-card rounded-3xl p-5 md:p-6">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">
              Now Playing
            </p>
            {current ? (
              <div className="mt-3 space-y-3">
                <h3 className="text-xl font-semibold">{current.title}</h3>
                <p className="albacat-muted text-sm">
                  {current.author} • {current.series} • Session {current.sessionNumber}
                </p>
                <p className="albacat-muted text-sm">{current.description}</p>
                <div className="flex flex-wrap gap-2">
                  <button
                    className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10 disabled:opacity-40"
                    onClick={() => previous && setSelectedId(previous.id)}
                    disabled={!previous}
                  >
                    Previous
                  </button>
                  <button
                    className="rounded-xl bg-sky-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
                    onClick={() => setSelectedId(current.id)}
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
              </div>
            ) : (
              <p className="albacat-muted mt-3 text-sm">No lecture selected yet.</p>
            )}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            {tab === 'browse' && (
              <div className="grid gap-4 md:grid-cols-2">
                {filtered.map((item) => (
                  <LectureCard
                    key={item.id}
                    item={item}
                    active={item.id === current?.id}
                    onPlay={() => setSelectedId(item.id)}
                  />
                ))}
              </div>
            )}

            {tab === 'playlist' && (
              <div className="albacat-card rounded-3xl p-5 md:p-6">
                <h2 className="text-2xl font-semibold">{current?.series ?? 'Series Playlist'}</h2>
                <p className="albacat-muted mt-2 text-sm">
                  Follow the sessions in order and move between them from the player.
                </p>
                <div className="mt-5 space-y-3">
                  {currentSeries.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setSelectedId(item.id)}
                      className={`w-full rounded-2xl border px-4 py-4 text-left transition ${
                        item.id === current?.id
                          ? 'border-sky-300/40 bg-sky-400/10'
                          : 'border-white/10 bg-white/5 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                        <div>
                          <p className="font-semibold">
                            Session {item.sessionNumber}: {item.title}
                          </p>
                          <p className="albacat-muted text-sm">{item.description}</p>
                        </div>
                        <span className="albacat-muted text-sm">{item.duration}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {tab === 'transcripts' && (
              <div className="space-y-4">
                {filtered.map((item) => (
                  <div key={item.id} className="albacat-card rounded-3xl p-5 md:p-6">
                    <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                      <div>
                        <h3 className="text-xl font-semibold">{item.title}</h3>
                        <p className="albacat-muted text-sm">
                          {item.author} • {item.series}
                        </p>
                      </div>
                      <button
                        className="rounded-xl bg-sky-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
                        onClick={() => setSelectedId(item.id)}
                      >
                        Open in Player
                      </button>
                    </div>
                    <p className="albacat-muted mt-4 text-sm leading-7">
                      {item.transcript || 'Transcript coming soon.'}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {tab === 'team' && (
              <div className="albacat-card rounded-3xl p-5 md:p-6">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">
                  Research & Development
                </p>
                <h2 className="mt-2 text-2xl font-semibold">{teamData.team_name}</h2>
                <p className="albacat-muted mt-3 text-sm leading-7">{teamData.mission}</p>
                <div className="mt-6 grid gap-4 md:grid-cols-2">
                  {teamData.members.map((member) => (
                    <div key={member.name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <h3 className="text-lg font-semibold">{member.name}</h3>
                      <p className="albacat-muted text-sm">{member.role}</p>
                      {member.organization ? (
                        <p className="albacat-muted mt-1 text-sm">{member.organization}</p>
                      ) : null}
                      {member.bio ? <p className="albacat-muted mt-3 text-sm">{member.bio}</p> : null}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <aside className="albacat-card rounded-3xl p-4 md:p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">
              Embedded Player
            </p>
            {current ? (
              <>
                <div className="mt-4 overflow-hidden rounded-2xl border border-white/10">
                  <iframe
                    title={current.title}
                    src={drivePreview(current.fileId)}
                    className="h-[420px] w-full bg-black"
                    allow="autoplay"
                  />
                </div>
                <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-semibold">{current.title}</h3>
                      <p className="albacat-muted text-sm">
                        {current.topic} • {current.duration}
                      </p>
                    </div>
                    <span className="rounded-full border border-sky-300/30 bg-sky-400/10 px-3 py-1 text-xs text-sky-200">
                      Session {current.sessionNumber}
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <p className="albacat-muted mt-4 text-sm">Select a lecture to start playback.</p>
            )}
          </aside>
        </section>
      </div>
    </main>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
      <p className="albacat-muted text-xs uppercase tracking-[0.18em]">{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  )
}

function TabButton({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode
  active?: boolean
  onClick: () => void
}) {
  return (
    <button
      className={`rounded-full px-4 py-2 text-sm font-medium transition ${
        active
          ? 'bg-sky-400 text-slate-950'
          : 'border border-white/10 bg-white/5 text-white hover:bg-white/10'
      }`}
      onClick={onClick}
    >
      {children}
    </button>
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
    <div
      className={`albacat-card rounded-3xl p-5 transition ${
        active ? 'ring-2 ring-sky-300/40' : ''
      }`}
    >
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

      <p className="albacat-muted mt-3 text-sm">
        {item.author} • {item.topic} • Session {item.sessionNumber}
      </p>

      <p className="albacat-muted mt-4 text-sm leading-7">{item.description}</p>

      <div className="mt-4 flex flex-wrap gap-2">
        {item.tags?.map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200"
          >
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
