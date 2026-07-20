// ============================================================================
// Frontend-Specific Dictionary Types
// ============================================================================

/** A curated popular entry shown in the HotEntries section. */
export interface HotEntry {
  entry_id: string
  title: string
  category: string
  snippet: string
}

/** An entry displayed in the DocumentViewer. */
export interface DocumentViewEntry {
  entry_id: string
  title: string
  content: string
  page: number | null
  category?: string
  chunk_id?: string
}

/** Parsed segment from answer text: either plain text or a citation marker. */
export interface CitationSegment {
  type: 'text' | 'citation'
  text: string
  title?: string
  page?: number | null
}

/** Confidence display configuration. */
export interface ConfidenceDisplay {
  label: string
  className: string
  color: string
}
