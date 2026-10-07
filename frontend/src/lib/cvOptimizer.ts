import type { CvSuggestion } from '@/lib/api'

export type SuggestionStatus = 'pending' | 'accepted' | 'rejected'

/** Choix de l'utilisateur sur une proposition ; `text` peut avoir été modifié avant acceptation. */
export interface SuggestionDecision {
  status: SuggestionStatus
  text: string
}

export type CvExportFormat = 'txt' | 'md'

/**
 * CV optimisé : chaque proposition acceptée remplace son extrait d'origine (première occurrence).
 * Un extrait introuvable (déjà réécrit par une proposition qui le chevauche) est ignoré et signalé.
 */
export function applySuggestions(
  cvText: string,
  suggestions: CvSuggestion[],
  decisions: Record<string, SuggestionDecision>,
): { text: string; applied: number; skipped: string[] } {
  let text = cvText
  let applied = 0
  const skipped: string[] = []
  for (const suggestion of suggestions) {
    const decision = decisions[suggestion.id]
    if (decision?.status !== 'accepted') continue
    const index = text.indexOf(suggestion.original)
    if (index === -1) {
      skipped.push(suggestion.id)
      continue
    }
    text = text.slice(0, index) + decision.text.trim() + text.slice(index + suggestion.original.length)
    applied += 1
  }
  return { text, applied, skipped }
}

/** Texte exporté : puces typographiques converties en listes Markdown pour le format .md. */
export function formatOptimizedCv(text: string, format: CvExportFormat): string {
  const body = format === 'md' ? text.replace(/^(\s*)[•▪●◦–](\s+)/gm, '$1-$2') : text
  return `${body.trim()}\n`
}

export function downloadOptimizedCv(text: string, format: CvExportFormat, basename: string) {
  const type = format === 'md' ? 'text/markdown' : 'text/plain'
  const blob = new Blob([formatOptimizedCv(text, format)], { type: `${type};charset=utf-8` })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${basename}.${format}`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
