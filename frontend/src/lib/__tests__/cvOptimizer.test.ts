import { describe, expect, it } from 'vitest'
import type { CvSuggestion } from '@/lib/api'
import { applySuggestions, formatOptimizedCv, type SuggestionDecision } from '@/lib/cvOptimizer'

const CV = 'Jeanne Martin\n• Développement d’API Python\n• Tests automatisés\nCompétences : Python, SQL'

function suggestion(id: string, original: string, proposed: string): CvSuggestion {
  return { id, original, proposed, section: '', requirement: '', rationale: '' }
}

const S1 = suggestion('s1', 'Développement d’API Python', 'Conception d’API REST en Python')
const S2 = suggestion('s2', 'Tests automatisés', 'Tests automatisés intégrés à la CI')

describe('applySuggestions', () => {
  it('remplace uniquement les extraits acceptés, avec le texte éventuellement modifié', () => {
    const decisions: Record<string, SuggestionDecision> = {
      s1: { status: 'accepted', text: 'Conception d’API REST en Python (FastAPI)' },
      s2: { status: 'rejected', text: S2.proposed },
    }
    const result = applySuggestions(CV, [S1, S2], decisions)
    expect(result.text).toBe('Jeanne Martin\n• Conception d’API REST en Python (FastAPI)\n• Tests automatisés\nCompétences : Python, SQL')
    expect(result.applied).toBe(1)
    expect(result.skipped).toEqual([])
  })

  it('laisse le CV intact sans proposition acceptée', () => {
    expect(applySuggestions(CV, [S1, S2], { s1: { status: 'pending', text: S1.proposed } }).text).toBe(CV)
  })

  it('signale un extrait déjà réécrit par une proposition qui le chevauche', () => {
    const overlapping = suggestion('s3', 'API Python', 'API Python et Go')
    const decisions: Record<string, SuggestionDecision> = {
      s1: { status: 'accepted', text: S1.proposed },
      s3: { status: 'accepted', text: overlapping.proposed },
    }
    const result = applySuggestions(CV, [S1, overlapping], decisions)
    expect(result.applied).toBe(1)
    expect(result.skipped).toEqual(['s3'])
  })
})

describe('formatOptimizedCv', () => {
  it('convertit les puces en liste Markdown pour le format .md', () => {
    expect(formatOptimizedCv(CV, 'md')).toContain('\n- Tests automatisés\n')
    expect(formatOptimizedCv(CV, 'txt')).toBe(`${CV}\n`)
  })
})
