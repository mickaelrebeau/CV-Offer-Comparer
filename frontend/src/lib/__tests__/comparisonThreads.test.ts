import { describe, expect, it } from 'vitest'
import type { ComparisonHistoryItem } from '@/lib/api'
import { groupThreads } from '@/lib/comparisonThreads'

function item(id: string, thread_id: string, version: number, thread_size: number): ComparisonHistoryItem {
  return {
    id,
    thread_id,
    version,
    thread_size,
    parent_comparison_id: null,
    offer_excerpt: '',
    cv_excerpt: '',
    offer_url: null,
    match_percentage: 0,
    total_items: 0,
    matches: 0,
    missing: 0,
    unclear: 0,
    created_at: null,
  }
}

describe('groupThreads', () => {
  it('regroupe les versions sous la plus récente, dans l’ordre du listing', () => {
    const v3 = item('c3', 'c1', 3, 3)
    const other = item('d1', 'd1', 1, 1)
    const v2 = item('c2', 'c1', 2, 3)
    const v1 = item('c1', 'c1', 1, 3)

    expect(groupThreads([v3, other, v2, v1])).toEqual([
      { id: 'c1', head: v3, previous: [v2, v1], size: 3 },
      { id: 'd1', head: other, previous: [], size: 1 },
    ])
  })

  it('traite un élément sans fil comme une analyse isolée', () => {
    const legacy = { ...item('x', '', 1, 1), thread_id: undefined, thread_size: undefined }
    expect(groupThreads([legacy])).toEqual([{ id: 'x', head: legacy, previous: [], size: 1 }])
  })
})
