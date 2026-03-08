'use client'
import Image from 'next/image'
import { useEffect, useMemo, useRef, useState } from 'react'
import catalog from '@/data/catalog.json'
import team from '@/data/team.json'

const lectures = catalog
const teamData = team

function StatCard({ label, value }) {
  return <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4"><p className="alb-muted text-xs uppercase tracking-[0.18em]">{label}</p><p className="mt-2 text-2xl font-bold">{value}</p></div>
}

function FloatingPlayer({ current, audioRef, onPrev, onNext, hasPrev, hasNext }) {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-white/10 bg-slate-950/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0">
          <p className="truncate font-semibold">{current.title}</p>
          <p className="alb-muted truncate text-sm">{current.author} • {current.series} • {current.language}</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={onPrev} disabled={!hasPrev} className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm disabled:opacity-40">Prev</button>
          <button onClick={() => audioRef.current?.play()} className="rounded-lg bg-sky-400 px-3 py-2 text-sm font-semibold text-slate-950">Play</button>
          <button onClick={onNext} disabled={!hasNext} className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm disabled:opacity-40">Next</button>
        </div>
        <div className="w-full md:w-[420px]">
          <audio ref={audioRef} controls className="w-full" key={current.audioUrl}>
            <source src={current.audioUrl} type="audio/mpeg" />
          </audio>
        </div>
      </div>
    </div>
  )
}

function LectureCard({ item, onPlay, active }) {
  return (
    <div className={`alb-card rounded-[28px] p-5 ${active ? 'ring-2 ring-sky-300/35' : ''}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-300">{item.series}</p>
          <h3 className="mt-2 text-xl font-semibold">{item.title}</h3>
        </div>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs">{item.duration}</span>
      </div>
      <p className="alb-muted mt-3 text-sm">{item.author} • {item.topic} • {item.language} • Session {item.sessionNumber}</p>
      <p className="alb-muted mt-4 text-sm leading-7">{item.description}</p>
      <div className="mt-4 flex flex-wrap gap-2">{(item.tags || []).map((tag) => <span key={tag} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">{tag}</span>)}</div>
      <div className="mt-5 flex gap-3">
        <button className="rounded-xl bg-sky-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300" onClick={onPlay}>Play</button>
        <a href={item.audioUrl} download className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10">Download</a>
      </div>
    </div>
  )
}

function ScholarProfile() {
  return (
    <section className="alb-card rounded-[28px] p-5 md:p-6">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">Scholar Inspiration</p>
      <h2 className="mt-2 text-2xl font-semibold">Sheik Albani Zaria</h2>
      <p className="alb-muted mt-3 text-sm leading-7">
        Project ALBACAT is inspired by the teachings of Sheik Albani Zaria. ALBACAT means Albani’s Catalog, reflecting a mission of preserving organized Islamic knowledge in a clean and accessible digital format.
      </p>
    </section>
  )
}

export default function PlayerApp() {
  const [query, setQuery] = useState('')
  const [selectedTopic, setSelectedTopic] = useState('All')
  const [selectedSeries, setSelectedSeries] = useState('All')
  const [selectedId, setSelectedId] = useState(lectures[0]?.id ?? '')
  const audioRef = useRef(null)

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
      const p = audioRef.current.play()
      if (p && typeof p.catch === 'function') p.catch(() => {})
    }
  }, [selectedId])

  const topics = useMemo(() => ['All', ...Array.from(new Set(lectures.map((x) => x.topic))).sort()], [])
  const seriesOptions = useMemo(() => ['All', ...Array.from(new Set(lectures.map((x) => x.series))).sort()], [])

  const filtered = useMemo(() => {
    return lectures.filter((item) => {
      if (selectedTopic !== 'All' && item.topic !== selectedTopic) return false
      if (selectedSeries !== 'All' && item.series !== selectedSeries) return false
      const haystack = [item.title, item.author, item.series, item.topic, item.description, item.transcript || '', ...(item.tags || [])].join(' ').toLowerCase()
      return haystack.includes(query.toLowerCase())
    }).sort((a, b) => a.sessionNumber - b.sessionNumber)
  }, [query, selectedTopic, selectedSeries])

  const current = lectures.find((x) => x.id === selectedId) || filtered[0] || lectures[0]
  const currentSeries = useMemo(() => current ? lectures.filter((x) => x.series === current.series).sort((a, b) => a.sessionNumber - b.sessionNumber) : [], [current])
  const idx = currentSeries.findIndex((x) => x.id === current?.id)
  const prev = idx > 0 ? currentSeries[idx - 1] : null
  const next = idx >= 0 && idx < currentSeries.length - 1 ? currentSeries[idx + 1] : null

  return (
    <main className="min-h-screen px-4 py-5 pb-36 md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="alb-card mb-6 rounded-[28px] p-5 md:p-7">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-3xl space-y-3">
              <div className="flex items-center gap-3">
                <div className="relative h-12 w-12 overflow-hidden rounded-2xl border border-white/10 bg-white/5">
                  <Image src="/logo.png" alt="Astrovia Systems" fill className="object-contain p-1" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.25em] text-sky-300">Astrovia Systems</p>
                  <p className="alb-muted text-sm">{teamData.organization?.slogan}</p>
                </div>
              </div>
              <h1 className="text-3xl font-bold leading-tight md:text-5xl">Project ALBACAT</h1>
              <p className="text-lg font-medium text-sky-300">Albani’s Catalog</p>
              <p className="alb-muted text-sm leading-7 md:text-base">
                Project ALBACAT is a structured Islamic library for preserving clean collections of Islamic books, lectures, Islamic sciences, and history. It is inspired by the teachings of Sheik Albani Zaria and fully developed and supported by Astrovia Systems.
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
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none placeholder:text-slate-400" placeholder="Search lectures, tags, transcript..." value={query} onChange={(e) => setQuery(e.target.value)} />
              <select className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" value={selectedTopic} onChange={(e) => setSelectedTopic(e.target.value)}>
                {topics.map((topic) => <option key={topic} value={topic} className="bg-slate-900">{topic}</option>)}
              </select>
              <select className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" value={selectedSeries} onChange={(e) => setSelectedSeries(e.target.value)}>
                {seriesOptions.map((series) => <option key={series} value={series} className="bg-slate-900">{series}</option>)}
              </select>
            </div>
          </aside>

          <div className="space-y-6">
            <section className="grid gap-6 xl:grid-cols-[1fr_380px]">
              <div className="alb-card rounded-[28px] p-4 md:p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">Now playing</p>
                <h2 className="mt-2 text-2xl font-semibold md:text-3xl">{current.title}</h2>
                <p className="alb-muted mt-2 text-sm">{current.author} • {current.series} • Session {current.sessionNumber}</p>
                <p className="alb-muted mt-3 max-w-3xl text-sm leading-7">{current.description}</p>
              </div>

              <div className="alb-card rounded-[28px] p-4 md:p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">Series playlist</p>
                <div className="mt-4 space-y-3">
                  {currentSeries.map((item) => (
                    <button key={item.id} onClick={() => setSelectedId(item.id)} className={`w-full rounded-2xl border px-4 py-4 text-left ${item.id === current?.id ? 'border-sky-300/35 bg-sky-400/10' : 'border-white/10 bg-white/5 hover:bg-white/10'}`}>
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

            <ScholarProfile />

            <section className="alb-card rounded-[28px] p-5 md:p-6">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">Research & Development</p>
              <h2 className="mt-2 text-2xl font-semibold">{teamData.team_name}</h2>
              <p className="alb-muted mt-3 text-sm leading-7">{teamData.mission}</p>
              <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="font-semibold">{teamData.organization?.name}</p>
                <p className="alb-muted text-sm">{teamData.organization?.slogan}</p>
              </div>
              <div className="mt-6 grid gap-4 md:grid-cols-2">
                {(teamData.members || []).map((member) => (
                  <div key={member.name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <h3 className="text-lg font-semibold">{member.name}</h3>
                    <p className="alb-muted text-sm">{member.role}</p>
                    <p className="alb-muted mt-1 text-sm">{member.organization}</p>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-300">Browse lectures</p>
                  <h2 className="text-2xl font-semibold">Catalog</h2>
                </div>
                <p className="alb-muted text-sm">{filtered.length} result(s)</p>
              </div>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {filtered.map((item) => <LectureCard key={item.id} item={item} active={item.id === current?.id} onPlay={() => setSelectedId(item.id)} />)}
              </div>
            </section>
          </div>
        </section>

        <FloatingPlayer current={current} audioRef={audioRef} onPrev={() => prev && setSelectedId(prev.id)} onNext={() => next && setSelectedId(next.id)} hasPrev={!!prev} hasNext={!!next} />
      </div>
    </main>
  )
}
