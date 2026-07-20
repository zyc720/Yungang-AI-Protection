import type { ConfidenceLevel } from '@/types/api'
import type { ConfidenceDisplay } from '@/types/dictionary'

const CONFIDENCE_MAP: Record<ConfidenceLevel, ConfidenceDisplay> = {
  high: {
    label: '可信度高',
    className: 'confidence-high',
    color: 'var(--color-confidence-high, #4A7C59)',
  },
  medium: {
    label: '可信度中',
    className: 'confidence-medium',
    color: 'var(--color-confidence-medium, #C4A035)',
  },
  low: {
    label: '可信度低',
    className: 'confidence-low',
    color: 'var(--color-confidence-low, #9B9B9B)',
  },
  not_found: {
    label: '未找到',
    className: 'confidence-not-found',
    color: 'var(--color-not-found, #D4C5B9)',
  },
}

export function useConfidenceStyle(level: ConfidenceLevel): ConfidenceDisplay {
  return CONFIDENCE_MAP[level] || CONFIDENCE_MAP.low
}
