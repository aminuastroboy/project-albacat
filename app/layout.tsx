import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Project ALBACAT',
  description: 'Islamic history audio library powered by Astrovia Systems.',
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
