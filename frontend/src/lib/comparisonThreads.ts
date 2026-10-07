import type { ComparisonHistoryItem } from '@/lib/api'

/** Analyses d'une même offre : la plus récente en tête, puis les versions précédentes chargées. */
export interface ComparisonThread {
  id: string
  head: ComparisonHistoryItem
  previous: ComparisonHistoryItem[]
  /** Nombre total de versions du fil (y compris celles hors de la page chargée) */
  size: number
}

/** Regroupe un listing (du plus récent au plus ancien) par fil de versions, dans l'ordre du listing. */
export function groupThreads(items: ComparisonHistoryItem[]): ComparisonThread[] {
  const threads = new Map<string, ComparisonThread>()
  for (const item of items) {
    const id = item.thread_id || item.id
    const thread = threads.get(id)
    if (thread) thread.previous.push(item)
    else threads.set(id, { id, head: item, previous: [], size: item.thread_size || 1 })
  }
  return [...threads.values()]
}
