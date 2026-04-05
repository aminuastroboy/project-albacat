import { Header, Footer } from '@/components/shared'
import LibraryView from '@/components/library-view'
import series from '@/data/series.json'
import { notFound } from 'next/navigation'
export default async function SeriesPage({params}){const {slug}=await params;const found=series.find(item=>item.slug===slug);if(!found)return notFound();return <main className='min-h-screen px-4 py-5 md:px-8'><div className='mx-auto max-w-7xl space-y-6'><Header /><div className='alb-card rounded-[32px] p-6'><div className='text-sm font-semibold uppercase tracking-[0.2em] text-sky-300'>Series Detail</div><h2 className='mt-2 text-3xl font-semibold'>{found.title}</h2><p className='alb-muted mt-3 text-sm leading-7'>{found.description}</p></div><LibraryView defaultSeriesSlug={slug} /><Footer /></div></main>}
