import type { CitationSegment } from '@/types/dictionary'

/**
 * Parse an LLM answer string into segments of text and citation markers.
 *
 * The backend returns answers with inline citations in the format:
 *   【来源：词条标题】 or 【来源：词条标题，页码 X】
 *
 * This composable splits the text so the UI can render citations as
 * clickable badges separate from plain text.
 */

// Matches 【来源：词条标题】 or 【来源：词条标题，页码 123】
const CITATION_RE = /【来源：(.+?)(?:，页码\s*(\d+))?】/g

export function useCitationParser(text: string): CitationSegment[] {
  const segments: CitationSegment[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  // Reset regex state
  CITATION_RE.lastIndex = 0

  while ((match = CITATION_RE.exec(text)) !== null) {
    // Add preceding text segment
    if (match.index > lastIndex) {
      const textBefore = text.slice(lastIndex, match.index)
      if (textBefore.trim()) {
        segments.push({ type: 'text', text: textBefore })
      }
    }

    // Add citation segment
    const title = match[1].trim()
    const page = match[2] ? parseInt(match[2], 10) : null
    segments.push({
      type: 'citation',
      text: match[0],
      title,
      page,
    })

    lastIndex = match.index + match[0].length
  }

  // Add remaining text after last citation
  if (lastIndex < text.length) {
    const remaining = text.slice(lastIndex)
    if (remaining.trim()) {
      segments.push({ type: 'text', text: remaining })
    }
  }

  // If no citations found, return the whole text as one segment
  if (segments.length === 0) {
    segments.push({ type: 'text', text })
  }

  return segments
}
