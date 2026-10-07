import { afterEach, describe, expect, it, vi } from 'vitest'
import posthog from 'posthog-js'
import { groupByStatus, offerExcerpt, printReport, reportFileTitle } from '@/lib/report'

vi.mock('posthog-js', () => ({ default: { capture: vi.fn() } }))

describe('offerExcerpt', () => {
  it("garde une offre courte telle quelle", () => {
    expect(offerExcerpt('  Développeur Vue  ')).toBe('Développeur Vue')
  })

  it('coupe une offre longue sur un mot', () => {
    const excerpt = offerExcerpt('mot '.repeat(50), 22)
    expect(excerpt).toBe('mot mot mot mot mot…')
  })
})

describe('groupByStatus', () => {
  it('regroupe manquants, à préciser puis correspondances, sans groupe vide', () => {
    const items = [
      { id: '1', status: 'match' },
      { id: '2', status: 'missing' },
      { id: '3', status: 'match' },
    ]
    expect(groupByStatus(items)).toEqual([
      { status: 'missing', items: [items[1]] },
      { status: 'match', items: [items[0], items[2]] },
    ])
  })

  it('classe les statuts inconnus dans « à préciser »', () => {
    expect(groupByStatus([{ status: 'partial' }])[0].status).toBe('unclear')
  })
})

describe('reportFileTitle', () => {
  it('inclut la date du rapport', () => {
    expect(reportFileTitle('Bilan', '2026-10-07T09:00:00Z')).toBe('Talento – Bilan – 2026-10-07')
  })
})

describe('printReport', () => {
  afterEach(() => vi.restoreAllMocks())

  it("suit l'export, imprime et restaure le titre du document", () => {
    const print = vi.spyOn(window, 'print').mockImplementation(() => {
      expect(document.title).toBe('Talento – Bilan')
    })
    document.title = 'Talento'

    printReport('interview', 'Talento – Bilan')

    expect(posthog.capture).toHaveBeenCalledWith('report_exported', { report_type: 'interview' })
    expect(print).toHaveBeenCalledOnce()
    window.dispatchEvent(new Event('afterprint'))
    expect(document.title).toBe('Talento')
  })
})
