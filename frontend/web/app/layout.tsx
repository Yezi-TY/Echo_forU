import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'DiffRhythm2 GUI',
  description: 'Music generation with DiffRhythm2',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

