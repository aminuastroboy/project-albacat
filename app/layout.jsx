import './globals.css'
export const metadata = {
  title:'Project ALBACAT',
  description:'Albani’s Catalog — a structured Islamic library for preserving lectures, books, Islamic sciences, and history.'
}
export default function RootLayout({ children }) {
  return <html lang="en"><body>{children}</body></html>
}
