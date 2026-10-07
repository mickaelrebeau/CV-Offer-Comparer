import posthog from 'posthog-js'

export type ReportType = 'comparison' | 'interview'

/** Offre et date d'un rapport : figées au lancement (ou lues dans l'historique), pas reprises du contexte courant. */
export interface ReportMeta {
  offerText: string
  offerUrl: string | null
  date: string
}

export const OFFER_EXCERPT_LENGTH = 600

/** Début de l'offre, coupé sur un mot, pour l'en-tête du rapport imprimé. */
export function offerExcerpt(text: string, max = OFFER_EXCERPT_LENGTH): string {
  const clean = text.trim().replace(/\n{3,}/g, '\n\n')
  if (clean.length <= max) return clean
  const cut = clean.slice(0, max)
  const lastSpace = cut.lastIndexOf(' ')
  return `${(lastSpace > max * 0.8 ? cut.slice(0, lastSpace) : cut).trimEnd()}…`
}

export type ReportStatus = 'missing' | 'unclear' | 'match'

/** Statut affiché : tout ce qui n'est ni « match » ni « missing » est à préciser (comme dans l'interface). */
export function reportStatus(status: string): ReportStatus {
  return status === 'match' || status === 'missing' ? status : 'unclear'
}

/** Éléments regroupés par statut, dans l'ordre du rapport : manquants, à préciser, puis correspondances. */
export function groupByStatus<T extends { status: string }>(items: T[]) {
  return (['missing', 'unclear', 'match'] as const)
    .map((status) => ({ status, items: items.filter((item) => reportStatus(item.status) === status) }))
    .filter((group) => group.items.length > 0)
}

/** Nom de fichier proposé par le navigateur (titre du document pendant l'impression). */
export function reportFileTitle(title: string, date: string): string {
  const day = new Date(date)
  const iso = Number.isNaN(day.getTime()) ? '' : day.toISOString().slice(0, 10)
  return ['Talento', title, iso].filter(Boolean).join(' – ')
}

/** Ouvre la boîte d'impression (« Enregistrer en PDF ») avec un titre de document adapté. */
export function printReport(type: ReportType, fileTitle: string) {
  posthog.capture('report_exported', { report_type: type })
  const previousTitle = document.title
  document.title = fileTitle
  const restore = () => {
    document.title = previousTitle
    window.removeEventListener('afterprint', restore)
  }
  window.addEventListener('afterprint', restore)
  window.print()
}
