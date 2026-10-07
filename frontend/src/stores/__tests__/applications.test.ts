import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import posthog from 'posthog-js'
import * as api from '@/lib/api'
import type { ApplicationDetail } from '@/lib/api'
import { useApplicationContextStore } from '@/stores/applicationContext'
import { useApplicationsStore } from '@/stores/applications'

vi.mock('posthog-js', () => ({ default: { capture: vi.fn(), reset: vi.fn(), identify: vi.fn() } }))
vi.mock('@/lib/api', () => ({
  APPLICATION_STATUSES: ['to_apply', 'applied', 'interview', 'offer', 'rejected'],
  listApplications: vi.fn(),
  createApplication: vi.fn(),
  updateApplication: vi.fn(),
  deleteApplication: vi.fn(),
}))

const OFFER = 'Développeur Python senior — Acme'

function application(overrides: Partial<ApplicationDetail> = {}): ApplicationDetail {
  return {
    id: 'app-1',
    title: 'Dev Python',
    company: 'Acme',
    offer_url: null,
    status: 'to_apply',
    notes: '',
    applied_at: null,
    created_at: null,
    updated_at: null,
    comparison_count: 0,
    interview_count: 0,
    cover_letter_count: 0,
    last_score: null,
    offer_text: OFFER,
    comparisons: [],
    interviews: [],
    cover_letters: [],
    ...overrides,
  }
}

beforeEach(() => {
  setActivePinia(createPinia())
  sessionStorage.clear()
  vi.clearAllMocks()
})

describe('applications', () => {
  it('suit la création sans contenu de l’offre', async () => {
    vi.mocked(api.createApplication).mockResolvedValue(application({ offer_url: 'https://jobs.example.com/1' }))
    const store = useApplicationsStore()

    await store.create({ comparison_id: 'c1' }, 'analysis')

    expect(store.items.map((item) => item.id)).toEqual(['app-1'])
    expect(posthog.capture).toHaveBeenCalledWith('application_created', { source: 'analysis', status: 'to_apply', has_offer_url: true })
    expect(JSON.stringify(vi.mocked(posthog.capture).mock.calls)).not.toContain(OFFER)
  })

  it('signale un changement de statut, pas une modification sans statut', async () => {
    vi.mocked(api.listApplications).mockResolvedValue({ items: [application()], total: 1 })
    const store = useApplicationsStore()
    await store.fetch()

    vi.mocked(api.updateApplication).mockResolvedValue(application({ status: 'applied' }))
    await store.setStatus('app-1', 'applied')
    expect(posthog.capture).toHaveBeenCalledWith('application_status_changed', { from_status: 'to_apply', to_status: 'applied' })
    expect(store.items[0].status).toBe('applied')

    vi.mocked(posthog.capture).mockClear()
    vi.mocked(api.updateApplication).mockResolvedValue(application({ status: 'applied', notes: 'Relance' }))
    await store.update('app-1', { notes: 'Relance' })
    expect(posthog.capture).not.toHaveBeenCalled()
  })

  it('met à jour le titre du contexte et oublie une candidature supprimée', async () => {
    const context = useApplicationContextStore()
    const store = useApplicationsStore()
    store.select(application())
    expect(context.applicationId).toBe('app-1')
    expect(context.offerText).toBe(OFFER)

    vi.mocked(api.updateApplication).mockResolvedValue(application({ title: 'Lead Python' }))
    await store.update('app-1', { title: 'Lead Python' })
    expect(context.applicationTitle).toBe('Lead Python')

    vi.mocked(api.deleteApplication).mockResolvedValue({ success: true })
    await store.remove('app-1')
    expect(context.applicationId).toBeNull()
  })
})
